#!/usr/bin/env python3
"""Run beginner prompts against the installed Codex CLI in isolated directories.

Usage: python3 scripts/run_agent_acceptance.py --case jargon --execute
Default previews the case and installation plan; --execute uses the user's CLI
model/auth configuration. Inputs are synthetic. Writes ignored evidence only.
Requires Python 3 and the official codex CLI. No external messages or deployments.
Each execution uses a new temporary directory and retains outputs for inspection.
"""

from __future__ import annotations

import argparse
import json
import shutil
import shlex
import sys
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "jargon": "小谷，扁平化管理是啥？我完全没用过AI。",
    "onboarding": "我没用过AI，想找工作，从哪开始？",
    "missing_resume": "小谷，帮我把简历改好一点，我不知道怎么弄。",
    "benefits": "小谷，这份工作靠谱吗？招聘说明：后端工程师，负责接口开发。税前月薪20K，14薪，五险一金按Base缴纳，双休但每周六上午有团队会议，带薪年假，还有周末团建。我不懂这些说法。",
    "resume": "小谷，帮我改成能投的简历。招聘说明：后端工程师，要求Python、SQL、HTTP接口。我的真实经历：我在课程项目中用Python读取CSV并清洗重复数据，用SQLite保存结果，用Flask写过一个查询接口。我负责这些代码，没有项目上线经历，没有性能提升数据。",
    "review": "小谷，我刚面试完，不知道哪里答得不好。下面是我记下来的完整问答：\n面试官：接口变慢时你怎么查？\n我回答：先去看日志，其他不太清楚。\n面试官：你做过什么项目？\n我回答：课程项目用Python清洗CSV，SQLite保存，Flask查询，我负责这些代码。没有上线过。\n面试官：你怎么证明优化有效？\n我回答：没有统计过，我不能说快了多少。",
}


def evaluate(final: str, workspace: Path, trace: Path) -> dict:
    events = []
    for line in trace.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    commands = [event.get("item", {}) for event in events if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "command_execution"]
    renderer_calls = [item for item in commands if "render_response.py" in item.get("command", "") and item.get("exit_code") == 0]
    rendered = ""
    if renderer_calls:
        # Compound shell commands can print file creation notices. Re-render the
        # actual payload through the canonical local renderer for comparison.
        tokens = shlex.split(renderer_calls[-1].get("command", ""))
        if len(tokens) >= 3 and tokens[1] in ("-lc", "-c"):
            tokens = shlex.split(tokens[2])
        for index, token in enumerate(tokens):
            if token.endswith("render_response.py") and index + 1 < len(tokens):
                payload = Path(tokens[index + 1])
                if not payload.is_absolute():
                    payload = workspace / payload
                if payload.is_file():
                    check = subprocess.run([sys.executable, str(ROOT / "skills/xiaogu-career-master/scripts/render_response.py"), str(payload)], capture_output=True, text=True)
                    if check.returncode == 0:
                        rendered = check.stdout
                        break
    return {
        "renderer_executed": bool(renderer_calls),
        "final_equals_renderer": bool(rendered) and final.strip() == rendered.strip(),
        "asks_user_to_run_commands": any(x in final for x in ("python3 ", "运行脚本", "编辑 JSON", "evidence_ids")),
        "workspace": str(workspace),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--codex", default="codex", help="Absolute CLI path when multiple installations exist")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"case": args.case, "prompt": CASES[args.case], "effect": "runs the existing codex CLI using synthetic input in a new temporary workspace"}, ensure_ascii=False, indent=2))
        return 0
    target = Path(tempfile.mkdtemp(prefix="xiaogu-acceptance-"))
    for name in ("xiaogu-career-master", "xiaogu-career-suite", "xiaogu-resume", "xiaogu-interview-review"):
        shutil.copytree(ROOT / "skills" / name, target / ".agents/skills" / name)
    (target / "AGENTS.md").write_text("本目录是求职助手试用目录。优先使用 .agents/skills 中的小谷技能。用户使用日常说法，不需要指定技能或命令。所有材料为虚构测试数据。只在本目录写入，不修改其他目录或向外部发送消息。\n", encoding="utf-8")
    evidence = ROOT / "evidence" / "beginner-acceptance-2026-10-01" / target.name
    evidence.mkdir(parents=True)
    final_path = evidence / "final.md"
    trace_path = evidence / "trace.jsonl"
    with trace_path.open("w", encoding="utf-8") as stdout, (evidence / "runtime.stderr").open("w", encoding="utf-8") as stderr:
        process = subprocess.run([args.codex, "exec", "--ephemeral", "--skip-git-repo-check", "-s", "workspace-write", "-C", str(target), "--json", "-o", str(final_path), CASES[args.case]], stdout=stdout, stderr=stderr, timeout=300)
    if process.returncode or not final_path.exists():
        result = {"case": args.case, "runtime_exit": process.returncode, "evidence": str(evidence)}
    else:
        result = {"case": args.case, "runtime_exit": 0, "evidence": str(evidence), **evaluate(final_path.read_text(encoding="utf-8"), target, trace_path)}
    (evidence / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("final_equals_renderer") and not result.get("asks_user_to_run_commands") else 1


if __name__ == "__main__":
    raise SystemExit(main())
