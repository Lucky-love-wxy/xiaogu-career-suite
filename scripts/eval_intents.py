#!/usr/bin/env python3
"""用真实模型评测 Web Agent 的路由（规则快路径 + 语义分类）。

Usage: python3 scripts/eval_intents.py tune|holdout
测试句为自拟，非真实用户数据（tests/fixtures/intent_phrasings.json）。每句单独新会话，n=1。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import agent  # noqa: E402

split = sys.argv[1] if len(sys.argv) > 1 else "tune"
cases = json.loads((ROOT / "tests/fixtures/intent_phrasings.json").read_text(encoding="utf-8"))[split]
provider = agent.DeepSeekProvider()
hits = 0
for case in cases:
    session = agent.Session()
    stored = session.absorb(case["q"])
    reg = agent.router.route(case["q"], session.context())
    if agent.regex_is_reliable(stored, case["q"], reg):
        by, intent = "regex", "jargon" if reg["pipeline"] == ["xiaogu-career-suite"] else "->".join(reg["pipeline"])
    else:
        by, (intent, role) = "llm", agent.classify(provider, case["q"], session, reg)
    ok = intent in case["expected"]
    hits += ok
    print(f"{'✓' if ok else '✗'} {by:<5} {intent:<17} 期望{'/'.join(case['expected']):<30} {case['q']}")
print(f"\n{split}: {hits}/{len(cases)}")
