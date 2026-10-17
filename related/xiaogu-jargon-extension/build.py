#!/usr/bin/env python3
"""把小谷权威黑话库打包进插件。

唯一数据源是 xiaogu-launch 运行时读取的那份词库；插件里不手改词条，
词库更新后重跑本脚本即可。输出 extension/data.js（content script 直接注入，
不走 fetch，省掉 web_accessible_resources 声明）。
"""
import json
import sys
from pathlib import Path

SOURCE = Path("/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/skills/xiaogu-career-suite/references/jargon.json")
OUT = Path(__file__).resolve().parent / "extension" / "data.js"

# 浮窗用得到的字段；其余字段（如 fields）不进包
KEEP = ("term", "aliases", "literal", "blunt", "worst_case", "red_flags", "verify", "good_answer", "evidence_boundary")


def main() -> int:
    entries = json.loads(SOURCE.read_text(encoding="utf-8"))
    slim = []
    for entry in entries:
        if not entry.get("term"):
            print(f"跳过无 term 的词条：{entry}", file=sys.stderr)
            continue
        slim.append({key: entry[key] for key in KEEP if key in entry})
    payload = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(
        "// 由 build.py 生成，勿手改。来源：" + str(SOURCE) + "\n"
        "globalThis.XG_JARGON = " + payload + ";\n",
        encoding="utf-8",
    )
    print(f"{len(slim)} 条词条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
