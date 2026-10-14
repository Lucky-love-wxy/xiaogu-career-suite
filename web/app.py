#!/usr/bin/env python3
"""小谷上线版服务：在 agent.Agent 外面加账号、额度、计量、停止开关、埋点和后台看板。

设计见 notes/2026-10-05-launch-platform-design.md。和本机模拟环境 server.py 的区别：
- 不再用全局锁：同一会话串行、不同用户并行（过程事件和用量都挂在请求上下文里，见 agent.EMIT / agent.USAGE）。
- 会话按用户归属存进数据库，重启不丢，别人拿到会话号也读不到。
- 每次模型调用按 DeepSeek 返回的 usage 记成本；每轮先预扣额度、结束后按实际成本结算。

启动（本机）：python3 web/app.py --port 8781
环境变量见 deploy/env.example。
"""

from __future__ import annotations

import argparse
import base64
import binascii
import dataclasses
import inspect
import json
import os
import queue
import secrets
import sys
import threading
import time
import urllib.request
from urllib.parse import urlsplit
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response, StreamingResponse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent  # noqa: E402
import ocr  # noqa: E402
from auth import Auth, AuthError, ConsoleSender  # noqa: E402
from store import FEATURES, Store, day_start, mask, now  # noqa: E402

STATIC = HERE / "static"
MAX_MESSAGE = 60_000          # 一条消息最多字符数（整份简历 + JD 足够）
RESERVE_CREDITS = 50          # 每轮预扣上限（¥0.5）；本轮扣费不超过它，超出部分记为平台损耗
MIN_START_CREDITS = 3         # 余额低于它不能开始新一轮
TOKEN_COOKIE, ADMIN_COOKIE = "xg_token", "xg_admin"
EVENT_NAMES = {"page_view", "feature_open", "resume_export", "interview_start", "interview_end",
               "credits_exhausted", "pay_open", "feedback_submit", "theme_change", "login_view"}


class Config:
    def __init__(self, env: dict | None = None):
        e = env if env is not None else os.environ
        self.env = e.get("XIAOGU_ENV", "dev")
        if self.env not in ("dev", "staging", "prod"):
            raise SystemExit(f"XIAOGU_ENV 只能是 dev / staging / prod，现在是 {self.env}")
        self.db = e.get("XIAOGU_DB") or str(HERE / "data" / f"xiaogu-{self.env}.db")
        # 测试环境默认不花钱：没显式指定就用模拟模型
        self.provider = e.get("XIAOGU_PROVIDER") or ("mock" if self.env == "staging" else "auto")
        self.secret = e.get("XIAOGU_SECRET") or ""
        self.admin_token = e.get("XIAOGU_ADMIN_TOKEN") or ""
        self.sender = e.get("XIAOGU_LOGIN_SENDER", "console")
        self.icp = e.get("XIAOGU_ICP_NO", "")                  # 网站 ICP 备案号，页脚公示
        self.model_filing = e.get("XIAOGU_MODEL_FILING", "")   # 所用大模型备案号，页脚公示
        self.signup_credits = int(e.get("XIAOGU_SIGNUP_CREDITS", "500"))
        if self.env == "prod":
            # 生产不允许静默降级成模拟模型：没有 key 就启动失败，而不是给真实用户看“（模拟模型）”回答
            if self.provider not in ("auto", "deepseek"):
                raise SystemExit(f"生产环境不能用 {self.provider} 模型")
            self.provider = "deepseek"
            host = urlsplit(e.get("XIAOGU_BASE_URL") or "https://api.deepseek.com").hostname
            if host != "api.deepseek.com" and e.get("XIAOGU_ALLOW_THIRD_PARTY_ROUTER") != "1":
                # 第三方中转站：用户对话和简历会经过一家未备案的第三方，且无法公示所用模型的备案号（RUNBOOK B7）
                raise SystemExit(f"生产环境的模型地址是第三方 {host}，不是 DeepSeek 官方；确认合规后设 "
                                 "XIAOGU_ALLOW_THIRD_PARTY_ROUTER=1 才能启动，见 RUNBOOK B7")
            if "simulated_live_sources(" in inspect.getsource(agent.Agent):
                # 从业者来源仍读 examples/ 下的模拟帖子，不能给真实用户看（deploy/RUNBOOK.md 阻塞项 B5）
                raise SystemExit("从业者来源还是模拟数据（agent.simulated_live_sources），关掉或接入真实来源后才能上生产，见 RUNBOOK B5")
            missing = [k for k, v in (("XIAOGU_SECRET", self.secret), ("XIAOGU_ADMIN_TOKEN", self.admin_token)) if not v]
            if missing:
                raise SystemExit(f"生产环境缺少 {', '.join(missing)}")
            if self.sender == "console":
                # 控制台验证码只打印在服务器日志里，真实用户收不到：生产环境必须先接短信或邮件服务
                raise SystemExit("生产环境不能用 console 验证码发送器；先接入短信 / 邮件服务（设计文档第 6 节问题 1）")
            drafts = [p.name for p in STATIC.glob("legal-*.html") if "<!-- DRAFT" in p.read_text(encoding="utf-8")]
            if drafts:
                raise SystemExit(f"用户协议 / 隐私政策还是草稿（{', '.join(drafts)}），确认内容并删掉 DRAFT 标记后才能上生产")
        if not self.secret:
            self.secret = "dev-only-secret"


def feature_of(trace: dict) -> str:
    """一轮结束后按实际路由归到三大功能之一，用于统计。"""
    intent = trace.get("intent") or ""
    route = trace.get("route") or {}
    task = route.get("task") or ""
    last = (route.get("pipeline") or [""])[-1]
    if task == "practice" or intent.startswith("interview") or last == "xiaogu-interview-review":
        return "interview"
    if task in ("tailor", "polish", "resume") or intent.startswith("resume") or last == "xiaogu-resume":
        return "resume"
    return "chat"


def guess_feature(session: agent.Session | None, message: str) -> str:
    """一轮开始前用确定性规则猜功能，给单功能开关用。模型分类出来的路由可能和这里不同，以统计为准。"""
    if session and (session.practice or session.last_question == agent.MISSING_QUESTIONS.get("想练的岗位")):
        return "interview"
    if agent.iv.START.search(message) or ("面试" in message and "复盘" in message):
        return "interview"
    if agent.rt.looks_like_resume(message) or "简历" in message:
        return "resume"
    return "chat"


class Platform:
    """服务的全部状态。测试里可以直接构造，传入假的 provider 和内存数据库。"""

    def __init__(self, config: Config, provider=None, store: Store | None = None, sender=None):
        self.config = config
        if provider is None:
            os.environ["XIAOGU_PROVIDER"] = config.provider
        self.agent = agent.Agent(provider=provider)
        self.store = store or Store(config.db, env=config.env)
        if str(config.db) != ":memory:":
            # 库外黑话待审清单放在数据库旁（web/data/，不进 git）；只记用户问的那个说法，不记会话
            self.agent.jargon_queue_dir = Path(config.db).parent
        self.auth = Auth(self.store, sender or ConsoleSender(), config.secret)
        self.locks: dict[str, threading.Lock] = {}
        self.locks_guard = threading.Lock()
        self.owners: dict[str, str] = {}      # 内存里的会话 → 用户，避免每轮查库
        self.admin_sessions: set[str] = set()
        self.provider_balance: dict | None = None

    # ------------------------------------------------------------ 会话

    def lock_for(self, session_id: str) -> threading.Lock:
        with self.locks_guard:
            return self.locks.setdefault(session_id, threading.Lock())

    def owned_session(self, user_id: str, session_id: str | None) -> agent.Session | None:
        """取用户自己的会话；不是他的会话一律当不存在。内存里没有就从数据库恢复。"""
        if not session_id:
            return None
        owner = self.owners.get(session_id) or self.store.session_owner(session_id)
        if owner != user_id:
            raise HTTPException(404, "会话不存在")
        if session_id not in self.agent.sessions:
            state = self.store.load_session(session_id)
            if state is None:
                raise HTTPException(404, "会话不存在")
            known = {f.name for f in dataclasses.fields(agent.Session)}
            self.agent.sessions[session_id] = agent.Session(**{k: v for k, v in state.items() if k in known})
        self.owners[session_id] = user_id
        return self.agent.sessions[session_id]

    # ------------------------------------------------------------ 开关

    def check_open(self, user: dict, feature: str) -> None:
        flags = self.store.flags()
        if flags.get("maintenance") == "1":
            raise HTTPException(503, flags.get("maintenance_reason") or "小谷暂停服务中，请稍后再来")
        # 全站 token 总上限：所有用户共用一个池子，用完就停，和个人 credits 无关。
        # 这里直接拦，而不只靠 breaker 打开的 maintenance——后台手动解除暂停但没调高上限时也不会放行
        cap = int(float(flags.get("global_token_cap") or 0))
        if cap and self.store.tokens_used() >= cap:
            raise HTTPException(503, "小谷本期的服务额度已经用完，暂停使用，请稍后再来")
        if user["status"] != "active":
            raise HTTPException(403, "你的账号已被暂停使用，如有疑问请联系我们")
        if flags.get(f"feature.{feature}", "1") != "1":
            name = {"chat": "对话", "resume": "简历", "interview": "模拟面试"}[feature]
            raise HTTPException(503, f"{name}功能暂时关闭，其他功能可以照常使用")

    def breaker(self) -> None:
        """自动熔断：全站 token 总上限、当日成本或模型账户余额越线，打开全局停止。每轮结算后和余额轮询时调用。"""
        flags = self.store.flags()
        if flags.get("maintenance") == "1":
            return
        token_cap = int(float(flags.get("global_token_cap") or 0))
        used = self.store.tokens_used()
        if token_cap and used >= token_cap:
            self._trip(f"全站累计 token {used:,} 已达总上限 {token_cap:,}，自动暂停")
            return
        cap = float(flags.get("daily_cost_cap_cny") or 0)
        spent = self.store.cost_since(day_start(0))
        if cap and spent >= cap:
            self._trip(f"今日模型成本 ¥{spent:.2f} 已达上限 ¥{cap:.2f}，自动暂停")
            return
        bal = self.provider_balance or {}
        if bal.get("kind") == "newapi":
            # 中转站额度按它自己的换算（quota_per_unit 点 = 1 美元）显示，阈值也用美元
            floor = float(flags.get("min_provider_balance_usd") or 0)
            left = bal.get("available_usd")
            if floor and not bal.get("unlimited") and left is not None and left < floor:
                self._trip(f"中转站剩余额度 ${left:.2f} 低于 ${floor:.2f}，自动暂停")
            return
        floor = float(flags.get("min_provider_balance_cny") or 0)
        cny = bal.get("total_cny")
        if floor and cny is not None and cny < floor:
            self._trip(f"DeepSeek 账户余额 ¥{cny:.2f} 低于 ¥{floor:.2f}，自动暂停")

    def _trip(self, reason: str) -> None:
        self.store.set_flag("maintenance", "1", "breaker")
        self.store.set_flag("maintenance_reason", reason, "breaker")
        self.store.event(None, "breaker_trip", {"reason": reason})
        print(f"[breaker] {reason}", file=sys.stderr, flush=True)

    def poll_provider_balance(self) -> None:
        """查模型账户余额。官方 DeepSeek 走 GET /user/balance（2026-10-05 核对官方文档）；
        其他 base_url 按 new-api 系中转站处理（见 poll_newapi_usage）。模拟模型没有余额。"""
        provider = self.agent.provider
        if provider.name != "deepseek":
            self.provider_balance = None
            return
        if urlsplit(provider.base_url).hostname != "api.deepseek.com":
            self.poll_newapi_usage(provider)
            return
        req = urllib.request.Request(f"{provider.base_url}/user/balance",
                                     headers={"Authorization": f"Bearer {provider._key}", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
        except Exception as exc:  # 查不到余额不影响服务，只在看板上显示“暂时查不到”
            self.provider_balance = {"error": type(exc).__name__, "checked_at": now()}
            return
        cny = next((b for b in data.get("balance_infos", []) if b.get("currency") == "CNY"), None)
        self.provider_balance = {
            "available": data.get("is_available"),
            "total_cny": float(cny["total_balance"]) if cny else None,
            "granted_cny": float(cny["granted_balance"]) if cny else None,
            "topped_up_cny": float(cny["topped_up_balance"]) if cny else None,
            "checked_at": now(),
        }
        self.breaker()

    def poll_newapi_usage(self, provider) -> None:
        """new-api 系中转站：用调用模型的同一把 key 读这把 key 的用量（GET /api/usage/token/，new-api 文档
        token-management/usage-token-get）。数值是中转站内部额度点，按公开的 /api/status 里 quota_per_unit
        （new-api 默认 500000 点 = 1 美元）换算成美元。返回字段名在文档里没有示例，2026-10-06 按源码习惯写，
        待用真 key 核对一次；读不到的字段显示为空，不猜。"""
        parts = urlsplit(provider.base_url)
        origin = f"{parts.scheme}://{parts.netloc}"

        def get(path: str, auth: bool) -> dict:
            headers = {"Accept": "application/json"}
            if auth:
                headers["Authorization"] = f"Bearer {provider._key}"
            with urllib.request.urlopen(urllib.request.Request(origin + path, headers=headers), timeout=15) as resp:
                return json.load(resp)

        try:
            status = get("/api/status", auth=False).get("data") or {}
            body = get("/api/usage/token/", auth=True)
        except Exception as exc:
            self.provider_balance = {"kind": "newapi", "host": parts.hostname, "error": type(exc).__name__, "checked_at": now()}
            return
        data = body.get("data") if isinstance(body.get("data"), dict) else body
        unit = float(status.get("quota_per_unit") or 500000)

        def usd(key: str):
            value = data.get(key)
            return round(float(value) / unit, 4) if isinstance(value, (int, float)) else None

        self.provider_balance = {
            "kind": "newapi", "host": parts.hostname, "name": data.get("name"),
            "used_usd": usd("total_used"), "available_usd": usd("total_available"), "granted_usd": usd("total_granted"),
            "unlimited": bool(data.get("unlimited_quota")), "expires_at": data.get("expires_at"),
            "quota_per_unit": unit, "ok": body.get("code", body.get("success", True)) not in (False, 0),
            "message": body.get("message") if body.get("code") is False or body.get("success") is False else None,
            "checked_at": now(),
        }
        self.breaker()

    # ------------------------------------------------------------ 一轮对话

    def prepare(self, user: dict, session_id: str | None, message: str) -> tuple[agent.Session | None, str, int, str]:
        """开始前的全部检查，失败抛 HTTPException（流式接口在开流之前就能返回错误码）。"""
        message = message.strip()
        if not message:
            raise HTTPException(400, "消息是空的")
        if len(message) > MAX_MESSAGE:
            raise HTTPException(413, "内容太长，请分段发送")
        session = self.owned_session(user["id"], session_id)
        feature = guess_feature(session, message)
        self.check_open(user, feature)
        turn_id = secrets.token_hex(8)
        reserved = self.store.reserve(user["id"], RESERVE_CREDITS, MIN_START_CREDITS, turn_id)
        if not reserved:
            self.store.event(user["id"], "credits_exhausted", {})
            raise HTTPException(402, "额度已用完。内测期间可以联系我们补充额度")
        return session, feature, reserved, turn_id

    def run(self, user: dict, session: agent.Session | None, message: str, scenario: str | None,
            reserved: int, turn_id: str, emit=None) -> dict[str, Any]:
        """执行一轮并结算。无论成功失败都会退回预扣、记下成本。"""
        calls: list[dict] = []
        token = agent.USAGE.set(calls)
        lock = self.lock_for(session.id) if session else None
        result: dict[str, Any] | None = None
        status = "error"
        try:
            if lock:
                lock.acquire()
            # 基本情况卡片每轮现读：用户改了马上生效，清空后也不会残留在会话里
            result = self.agent.handle(session.id if session else None, message.strip(), scenario, emit=emit,
                                       card=self.store.get_profile(user["id"]))
            status = result["status"]
        finally:
            if lock:
                lock.release()
            agent.USAGE.reset(token)
            trace = (result or {}).get("trace") or {}
            sid = (result or {}).get("session_id") or (session.id if session else "")
            cost = self.store.record_turn({
                "id": turn_id, "user_id": user["id"], "session_id": sid, "feature": feature_of(trace) if result else "chat",
                "intent": trace.get("intent"), "status": status, "ms": trace.get("ms"),
                "user_message": message.strip(), "final_text": (result or {}).get("text"),
            }, calls)
            # 校验失败最终“受阻”、服务出错：不向用户收费，成本照记
            charge = min(reserved, self.store.charge_for(cost)) if status in ("complete", "needs_input") else 0
            self.store.settle(user["id"], reserved, charge, turn_id)
            self.store.set_turn_charge(turn_id, charge)
            if sid and sid in self.agent.sessions:
                self.owners[sid] = user["id"]
                state = dataclasses.asdict(self.agent.sessions[sid])
                self.store.save_session(sid, user["id"], state, message.strip().splitlines()[0])
            self.store.touch(user["id"])
            self.breaker()
        result["credits"] = {"charged": charge, "balance": self.store.balance(user["id"])}
        if self.config.env == "prod":
            result.pop("trace", None)  # 生产环境不把内部路由细节发给用户
        return result


def create_app(platform: Platform) -> FastAPI:
    cfg, store, auth = platform.config, platform.store, platform.auth
    app = FastAPI(title="xiaogu", docs_url=None, redoc_url=None, openapi_url=None)
    secure = cfg.env != "dev"

    @app.middleware("http")
    async def guard(request: Request, call_next):
        # 写操作只收 JSON：浏览器跨站表单发不出 application/json，配合 SameSite=Lax 防 CSRF
        if request.method in ("POST", "DELETE", "PUT") and request.url.path.startswith("/api/"):
            if not request.headers.get("content-type", "").startswith("application/json"):
                return JSONResponse({"error": "只接受 JSON"}, status_code=415)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException):
        return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

    def current_user(request: Request) -> dict:
        user = auth.user_for(request.cookies.get(TOKEN_COOKIE))
        if not user:
            raise HTTPException(401, "请先登录")
        return user

    def require_admin(request: Request) -> None:
        if not cfg.admin_token:
            raise HTTPException(403, "后台未启用：没有配置 XIAOGU_ADMIN_TOKEN")
        if request.cookies.get(ADMIN_COOKIE) not in platform.admin_sessions:
            raise HTTPException(401, "请先登录后台")

    def page(name: str) -> FileResponse:
        return FileResponse(STATIC / name, media_type="text/html; charset=utf-8", headers={"Cache-Control": "no-store"})

    # ------------------------------------------------------------ 页面

    @app.get("/")
    def home():
        return page("home.html")

    @app.get("/app")
    def app_page():
        return page("index.html")

    @app.get("/login")
    def login_page():
        return page("login.html")

    @app.get("/admin")
    def admin_page():
        return page("admin.html")

    @app.get("/legal/{name}")
    def legal(name: str):
        if name not in ("terms", "privacy"):
            raise HTTPException(404, "not found")
        return page(f"legal-{name}.html")

    @app.get("/static/{name}")
    def static_file(name: str):
        target = (STATIC / name).resolve()
        if STATIC not in target.parents or not target.is_file() or target.suffix not in (".css", ".js", ".svg"):
            raise HTTPException(404, "not found")
        return FileResponse(target)

    @app.get("/brand/{name}")
    def brand_file(name: str):
        """吉祥物等品牌图片。只认 static/brand 目录下的图片文件，长缓存。"""
        folder = STATIC / "brand"
        target = (folder / name).resolve()
        if folder not in target.parents or not target.is_file() or target.suffix not in (".webp", ".png", ".svg", ".jpg"):
            raise HTTPException(404, "not found")
        return FileResponse(target, headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/resume/{art_id}")
    def resume_page(art_id: str, request: Request):
        user = current_user(request)
        for row in store.list_sessions(user["id"]):
            session = platform.owned_session(user["id"], row["id"])
            if session and art_id in session.artifacts:
                return HTMLResponse(session.artifacts[art_id]["html"])
        raise HTTPException(404, "这份简历不存在或不属于你")

    # ------------------------------------------------------------ 公共信息

    @app.get("/api/meta")
    def meta():
        provider = platform.agent.provider
        flags = store.flags()
        return {"env": cfg.env, "provider": provider.name, "model": provider.model, "scenarios": agent.scenario_names(),
                "icp": cfg.icp, "model_filing": cfg.model_filing, "maintenance": flags.get("maintenance") == "1",
                "maintenance_reason": flags.get("maintenance_reason") if flags.get("maintenance") == "1" else "",
                "features": {f: flags.get(f"feature.{f}", "1") == "1" for f in FEATURES},
                "signup_open": flags.get("signup_open") == "1"}

    @app.get("/api/sample")
    def sample(request: Request):
        current_user(request)
        return {"jd": (agent.MOCK_DIR / "jd.txt").read_text(encoding="utf-8")}

    # ------------------------------------------------------------ 登录

    @app.post("/api/auth/code")
    def auth_code(data: dict = Body(...)):
        try:
            sent = auth.request_code(str(data.get("contact", "")))
        except AuthError as exc:
            raise HTTPException(400, str(exc)) from None
        body = {"ok": True, "new_user": sent["new_user"]}
        if cfg.env == "dev":
            body["dev_code"] = sent["_code"]  # 只在本机开发环境回显，方便自测
        return body

    @app.post("/api/auth/verify")
    def auth_verify(data: dict = Body(...)):
        try:
            user, token = auth.verify(str(data.get("contact", "")), str(data.get("code", "")),
                                      data.get("invite"), bool(data.get("consent")))
        except AuthError as exc:
            raise HTTPException(400, str(exc)) from None
        store.event(user["id"], "login_success", {"contact_type": "email" if "@" in user["contact"] else "phone"})
        response = JSONResponse({"ok": True})
        response.set_cookie(TOKEN_COOKIE, token, max_age=30 * 86400, httponly=True, samesite="lax", secure=secure)
        return response

    @app.post("/api/auth/logout")
    def auth_logout(request: Request):
        token = request.cookies.get(TOKEN_COOKIE)
        if token:
            auth.logout(token)
        response = JSONResponse({"ok": True})
        response.delete_cookie(TOKEN_COOKIE)
        return response

    @app.get("/api/me")
    def me(request: Request):
        user = current_user(request)
        return {"contact": mask(user["contact"]), "balance": store.balance(user["id"]), "theme": user["theme"],
                "status": user["status"]}

    @app.post("/api/me/theme")
    def set_theme(request: Request, data: dict = Body(...)):
        user = current_user(request)
        theme = data.get("theme")
        if theme not in ("mono", "wa"):
            raise HTTPException(400, "未知主题")
        with store.conn() as c:
            c.execute("UPDATE users SET theme=? WHERE id=?", (theme, user["id"]))
        return {"ok": True}

    @app.get("/api/me/profile")
    def get_profile(request: Request):
        """基本情况卡片：字段和可选值一起给前端，前端不写死第二份。"""
        user = current_user(request)
        fields = {k: {"max": n, "choices": c if isinstance(c, list) else (list(c) if c else None), "multi": isinstance(c, list)}
                  for k, (n, c) in agent.CARD_FIELDS.items()}
        return {"profile": store.get_profile(user["id"]), "fields": fields, "required": list(agent.CARD_REQUIRED),
                "done_message": agent.CARD_DONE}

    @app.post("/api/me/profile")
    def set_profile(request: Request, data: dict = Body(...)):
        """保存卡片；提交空卡片即清空（直接删行）。必填项缺了不保存，避免存一张给不出建议的卡。"""
        user = current_user(request)
        card = agent.clean_card(data.get("profile") if isinstance(data.get("profile"), dict) else {})
        missing = [k for k in agent.CARD_REQUIRED if k not in card]
        if card and missing:
            raise HTTPException(400, "请先填：" + "、".join(missing))
        store.set_profile(user["id"], card)
        return {"profile": card}

    # ------------------------------------------------------------ 会话

    @app.get("/api/sessions")
    def sessions(request: Request):
        return {"sessions": store.list_sessions(current_user(request)["id"])}

    @app.get("/api/sessions/{session_id}")
    def session_turns(session_id: str, request: Request):
        user = current_user(request)
        platform.owned_session(user["id"], session_id)
        rows = store.rows("SELECT user_message, final_text, status, created_at FROM turns WHERE session_id=? AND user_id=? "
                          "AND deleted_at IS NULL ORDER BY created_at", (session_id, user["id"]))
        return {"turns": rows}

    @app.delete("/api/sessions/{session_id}")
    def delete_session(session_id: str, request: Request):
        user = current_user(request)
        if not store.delete_session(user["id"], session_id):
            raise HTTPException(404, "会话不存在")
        platform.agent.sessions.pop(session_id, None)
        platform.owners.pop(session_id, None)
        return {"ok": True}

    @app.post("/api/events")
    def events(request: Request, data: dict = Body(...)):
        user = auth.user_for(request.cookies.get(TOKEN_COOKIE))
        name = str(data.get("name", ""))
        if name not in EVENT_NAMES:
            raise HTTPException(400, "未知事件")
        props = data.get("props") if isinstance(data.get("props"), dict) else {}
        store.event(user["id"] if user else None, name, props)
        return {"ok": True}

    # ------------------------------------------------------------ 对话

    @app.post("/api/chat")
    def chat(request: Request, data: dict = Body(...)):
        user = current_user(request)
        message, scenario = str(data.get("message", "")), data.get("scenario")
        if scenario and scenario not in agent.scenario_names():
            raise HTTPException(400, "unknown scenario")
        session, _feature, reserved, turn_id = platform.prepare(user, data.get("session_id"), message)
        try:
            return platform.run(user, session, message, scenario, reserved, turn_id)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(500, f"服务端出错：{type(exc).__name__}") from None

    @app.post("/api/chat/stream")
    def chat_stream(request: Request, data: dict = Body(...)):
        """SSE：过程阶段逐条推送，最后推送校验后的完整回答。检查不通过时在开流前直接返回错误码。"""
        user = current_user(request)
        message, scenario = str(data.get("message", "")), data.get("scenario")
        if scenario and scenario not in agent.scenario_names():
            raise HTTPException(400, "unknown scenario")
        session, _feature, reserved, turn_id = platform.prepare(user, data.get("session_id"), message)
        events_q: queue.Queue = queue.Queue()

        def work():
            try:
                result = platform.run(user, session, message, scenario, reserved, turn_id, emit=events_q.put)
                events_q.put({"type": "final", **result})
            except Exception as exc:
                events_q.put({"type": "error", "error": f"服务端出错：{type(exc).__name__}"})
            events_q.put(None)

        # 用户中途关页面：这一轮照常跑完、结算（钱已经花了，中途掐断用户什么也拿不到）
        threading.Thread(target=work, daemon=True).start()

        def stream():
            while (event := events_q.get()) is not None:
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(stream(), media_type="text/event-stream; charset=utf-8",
                                 headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

    # 模拟面试的纯文本接口（给以后的语音前端用），和网页聊天共用同一个状态机与计费

    @app.post("/api/interview/start")
    def interview_start(request: Request, data: dict = Body(...)):
        user = current_user(request)
        session_id = data.get("session_id")
        existing = platform.owned_session(user["id"], session_id)
        if existing and existing.practice:
            raise HTTPException(409, "这个会话已有进行中的模拟面试，用 /api/interview/answer 继续，或传“结束”打分")
        role = str(data.get("role") or "").strip()[:20]
        message = f"模拟面试：{role}" if role else "模拟面试"
        session, _f, reserved, turn_id = platform.prepare(user, session_id, message)
        result = platform.run(user, session, message, None, reserved, turn_id)
        return {k: result[k] for k in ("session_id", "say", "status", "practice", "credits")}

    @app.post("/api/interview/answer")
    def interview_answer(request: Request, data: dict = Body(...)):
        user = current_user(request)
        session = platform.owned_session(user["id"], data.get("session_id"))
        waiting = session and session.last_question == agent.MISSING_QUESTIONS.get("想练的岗位")
        if not (session and (session.practice or waiting)):
            raise HTTPException(409, "这个会话没有进行中的模拟面试，请先调用 /api/interview/start")
        message = str(data.get("text", ""))
        session, _f, reserved, turn_id = platform.prepare(user, session.id, message)
        result = platform.run(user, session, message, None, reserved, turn_id)
        return {k: result[k] for k in ("session_id", "say", "status", "practice", "credits")}

    @app.get("/api/interview/state")
    def interview_state(session_id: str, request: Request):
        user = current_user(request)
        session = platform.owned_session(user["id"], session_id)
        practice = session.practice if session else None
        if not practice:
            return {"active": False}
        q = practice["questions"][practice["i"]]
        return {"active": True, "question": practice["i"] + 1, "total": len(practice["questions"]),
                "stage": practice["stage"], "say": q["question"] if practice["stage"] == "main" else q["follow_up"]}

    @app.post("/api/ocr")
    def ocr_image(request: Request, data: dict = Body(...)):
        """截图 → 文字。只回填输入框由用户核对后发送，不进会话、不写日志、不扣额度（本机识别，不调模型）。"""
        user = current_user(request)
        platform.check_open(user, "chat")  # 对话关着时识别出来也发不出去
        raw = str(data.get("image", ""))
        try:
            image = base64.b64decode(raw.split(",", 1)[-1], validate=True)  # 兼容 data:image/...;base64, 前缀
        except (ValueError, binascii.Error):
            raise HTTPException(400, "图片数据不完整，请重新选择") from None
        try:
            text = ocr.recognize(image)
        except ocr.OcrError as exc:
            raise HTTPException(400, str(exc)) from None
        except ocr.OcrUnavailable:
            raise HTTPException(503, "图片识别暂时不可用，请先把文字复制进来") from None
        return {"text": text}

    # ------------------------------------------------------------ 后台

    @app.post("/api/admin/login")
    def admin_login(data: dict = Body(...)):
        if not cfg.admin_token:
            raise HTTPException(403, "后台未启用：没有配置 XIAOGU_ADMIN_TOKEN")
        if not secrets.compare_digest(str(data.get("token", "")), cfg.admin_token):
            time.sleep(1)  # 拖慢暴力尝试
            raise HTTPException(401, "口令不对")
        sid = secrets.token_urlsafe(32)
        platform.admin_sessions.add(sid)
        response = JSONResponse({"ok": True})
        response.set_cookie(ADMIN_COOKIE, sid, max_age=12 * 3600, httponly=True, samesite="strict", secure=secure,
                            path="/")
        return response

    @app.get("/api/admin/dashboard")
    def admin_dashboard(request: Request):
        require_admin(request)
        data = store.dashboard(platform.provider_balance)
        data["provider"] = {"name": platform.agent.provider.name, "model": platform.agent.provider.model}
        return data

    @app.post("/api/admin/refresh-balance")
    def admin_refresh_balance(request: Request):
        require_admin(request)
        platform.poll_provider_balance()
        return {"provider_balance": platform.provider_balance}

    @app.get("/api/admin/users/{user_id}/turns")
    def admin_user_turns(user_id: str, request: Request):
        require_admin(request)
        user = store.user(user_id)
        if not user:
            raise HTTPException(404, "没有这个用户")
        return {"user": {"id": user["id"], "contact": mask(user["contact"]), "status": user["status"],
                         "balance": store.balance(user_id)},
                "turns": store.user_turns(user_id),
                "ledger": store.rows("SELECT type, credits, note, created_at FROM credit_ledger WHERE user_id=? "
                                     "AND type NOT IN ('reserve','release') ORDER BY id DESC LIMIT 50", (user_id,))}

    @app.post("/api/admin/flags")
    def admin_flags(request: Request, data: dict = Body(...)):
        require_admin(request)
        key, value = str(data.get("key", "")), str(data.get("value", ""))
        try:
            store.set_flag(key, value, "admin")
            if key == "maintenance" and value == "0":
                store.set_flag("maintenance_reason", "", "admin")
        except KeyError:
            raise HTTPException(400, "未知开关") from None
        store.event(None, "admin_flag", {"key": key, "value": value})
        return {"flags": store.flags()}

    @app.post("/api/admin/users/{user_id}/status")
    def admin_user_status(user_id: str, request: Request, data: dict = Body(...)):
        require_admin(request)
        try:
            store.set_user_status(user_id, str(data.get("status")))
        except ValueError:
            raise HTTPException(400, "状态只能是 active 或 suspended") from None
        return {"ok": True}

    @app.post("/api/admin/users/{user_id}/credits")
    def admin_user_credits(user_id: str, request: Request, data: dict = Body(...)):
        require_admin(request)
        credits = int(data.get("credits") or 0)
        if not credits or abs(credits) > 100_000:
            raise HTTPException(400, "额度数不对")
        store.adjust_credits(user_id, credits, str(data.get("note") or "后台调整")[:100])
        return {"balance": store.balance(user_id)}

    @app.post("/api/admin/invites")
    def admin_invites(request: Request, data: dict = Body(...)):
        require_admin(request)
        count = max(1, min(50, int(data.get("count") or 1)))
        credits = int(data.get("credits") or cfg.signup_credits)
        codes = store.create_invites(count, credits, max(1, int(data.get("max_uses") or 1)), str(data.get("note") or "")[:60])
        return {"codes": codes}

    @app.post("/api/admin/prices")
    def admin_prices(request: Request, data: dict = Body(...)):
        require_admin(request)
        try:
            row = (str(data["model"]), float(data["input_per_m"]), float(data["cache_hit_per_m"]), float(data["output_per_m"]))
        except (KeyError, ValueError):
            raise HTTPException(400, "单价格式不对") from None
        with store.conn() as c:
            c.execute("INSERT INTO prices VALUES (?,?,?,?,?,?) ON CONFLICT(model) DO UPDATE SET input_per_m=excluded.input_per_m, "
                      "cache_hit_per_m=excluded.cache_hit_per_m, output_per_m=excluded.output_per_m, source=excluded.source, "
                      "updated_at=excluded.updated_at", (*row, "后台手动修改", now()))
        return {"ok": True}

    return app


def start_background(platform: Platform) -> None:
    """每 5 分钟查一次 DeepSeek 余额；每天清理一次超过 6 个月的已删除对话。"""
    def loop():
        last_purge = 0.0
        while True:
            platform.poll_provider_balance()
            if now() - last_purge > 86400:
                platform.store.purge()
                last_purge = now()
            time.sleep(300)
    threading.Thread(target=loop, daemon=True).start()


def main() -> int:
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("XIAOGU_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8781)))
    args = parser.parse_args()
    platform = Platform(Config())
    start_background(platform)
    print(f"xiaogu {platform.config.env} on http://{args.host}:{args.port}  provider={platform.agent.provider.name}  "
          f"db={platform.config.db}", flush=True)
    # 只监听本机；公网流量由 nginx 反代进来（deploy/nginx.conf）
    uvicorn.run(create_app(platform), host=args.host, port=args.port, log_level="warning", proxy_headers=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
