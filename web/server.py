#!/usr/bin/env python3
"""小谷 Web Agent 模拟环境的本地服务。

Usage: python3 web/server.py [--port 8765] [--provider auto|deepseek|mock]
只监听 127.0.0.1：服务端持有模型 key 且没有登录鉴权，不对局域网开放。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent  # noqa: E402

STATIC = HERE / "static"
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
MAX_BODY = 200_000


class Handler(BaseHTTPRequestHandler):
    server_version = "XiaoguSim/0.1"
    xiaogu: agent.Agent
    lock = threading.Lock()

    def log_message(self, fmt, *args):  # 只打印路径和状态，不打印请求体（可能含简历）
        sys.stderr.write(f"{self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}\n")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/meta":
            provider = self.xiaogu.provider
            return self._json(200, {"provider": provider.name, "model": provider.model, "scenarios": agent.scenario_names()})
        if path.startswith("/resume/"):
            # 排版好的简历成品页：内容在生成时已全部 html.escape
            page = self.xiaogu.artifact(path.rsplit("/", 1)[-1])
            if page is None:
                return self._json(404, {"error": "这份简历已不在当前会话里，请重新生成"})
            return self._send(200, page.encode("utf-8"), TYPES[".html"])
        if path == "/api/interview/state":
            session_id = (parse_qs(urlsplit(self.path).query).get("session_id") or [""])[0]
            session = self.xiaogu.sessions.get(session_id)
            practice = session.practice if session else None
            if not practice:
                return self._json(200, {"active": False})
            q = practice["questions"][practice["i"]]
            return self._json(200, {"active": True, "question": practice["i"] + 1, "total": len(practice["questions"]),
                                    "stage": practice["stage"], "say": q["question"] if practice["stage"] == "main" else q["follow_up"]})
        if path == "/api/sample":
            jd = (agent.MOCK_DIR / "jd.txt").read_text(encoding="utf-8")
            return self._json(200, {"jd": jd})
        target = (STATIC / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
        if STATIC not in target.parents or not target.is_file() or target.suffix not in TYPES:
            return self._json(404, {"error": "not found"})
        self._send(200, target.read_bytes(), TYPES[target.suffix])

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self._json(413, {"error": "内容太长，请分段发送"})
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "bad json"})
        if self.path in ("/api/interview/start", "/api/interview/answer"):
            return self._interview(data)
        if self.path not in ("/api/chat", "/api/chat/stream"):
            return self._json(404, {"error": "not found"})
        message = str(data.get("message", "")).strip()
        if not message:
            return self._json(400, {"error": "empty message"})
        scenario = data.get("scenario")
        if scenario and scenario not in agent.scenario_names():
            return self._json(400, {"error": "unknown scenario"})
        if self.path == "/api/chat/stream":
            return self._stream(data.get("session_id"), message, scenario)
        try:
            with self.lock:  # 会话表是内存字典，串行化写入
                result = self.xiaogu.handle(data.get("session_id"), message, scenario)
        except Exception as exc:  # 本地检索器等意外失败也给出可读结果
            return self._json(500, {"error": f"服务端出错：{type(exc).__name__}"})
        return self._json(200, result)

    def _interview(self, data: dict) -> None:
        """模拟面试的纯文本接口，给以后的语音前端用：语音端把话转成文字传 text，把返回的 say 读出来。
        和网页聊天走同一个状态机（Agent.handle），不另起一套逻辑。"""
        session_id = data.get("session_id")
        session = self.xiaogu.sessions.get(session_id or "")
        if self.path == "/api/interview/start":
            if session and session.practice:
                # 语音端断线重连时常重复调 start：不能把“模拟面试：岗位”记成一条回答
                return self._json(409, {"error": "这个会话已有进行中的模拟面试，用 /api/interview/answer 继续，或传“结束”打分"})
            role = str(data.get("role") or "").strip()[:20]
            message = f"模拟面试：{role}" if role else "模拟面试"
        else:
            message = str(data.get("text", "")).strip()
            waiting_role = session and session.last_question == agent.MISSING_QUESTIONS["想练的岗位"]
            if not (session and (session.practice or waiting_role)):
                return self._json(409, {"error": "这个会话没有进行中的模拟面试，请先调用 /api/interview/start"})
            if not message:
                return self._json(400, {"error": "empty text"})
        try:
            with self.lock:
                result = self.xiaogu.handle(session_id, message)
        except Exception as exc:
            return self._json(500, {"error": f"服务端出错：{type(exc).__name__}"})
        return self._json(200, {"session_id": result["session_id"], "say": result["say"], "status": result["status"],
                                "practice": result["practice"]})

    def _stream(self, session_id, message: str, scenario) -> None:
        """SSE：先逐条推送过程阶段，最后推送校验后的完整回答。回答正文只出现在 final 事件里。"""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        def emit(event: dict) -> None:
            try:
                self.wfile.write(f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8"))
                self.wfile.flush()
            except OSError:
                pass  # 浏览器中途关掉页面：后端照常算完、写日志

        try:
            with self.lock:
                result = self.xiaogu.handle(session_id, message, scenario, emit=emit)
            emit({"type": "final", **result})
        except Exception as exc:
            emit({"type": "error", "error": f"服务端出错：{type(exc).__name__}"})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8765)))
    parser.add_argument("--provider", choices=("auto", "deepseek", "mock"), default=os.environ.get("XIAOGU_PROVIDER", "auto"))
    args = parser.parse_args()
    os.environ["XIAOGU_PROVIDER"] = args.provider
    Handler.xiaogu = agent.Agent(log_dir=HERE / "logs")  # 本地运行日志，已在 .gitignore
    print(f"xiaogu sim on http://127.0.0.1:{args.port}  provider={Handler.xiaogu.provider.name}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
