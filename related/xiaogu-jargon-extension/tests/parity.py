#!/usr/bin/env python3
"""插件匹配器 vs 小谷 search.py 一致性检查（对 50 条校招 JD 样本）。

插件命中集合必须是 search.py 的子集；少掉的只允许来自
「长词已占位」或「否定跳过」两种设计差异，逐条打印供人工过目。
"""
import json, subprocess, sys
from pathlib import Path

LAUNCH = Path("/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch")
sys.path.insert(0, str(LAUNCH / "skills/xiaogu-career-suite/scripts"))
from search import search_jargon  # noqa: E402

HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (LAUNCH / "data/jargon_eval/campus_sample.jsonl").open(encoding="utf-8")]
js = r"""
const {compile, match} = require(process.argv[1]);
const fs = require('fs');
const raw = fs.readFileSync(process.argv[2], 'utf8');
const E = JSON.parse(raw.slice(raw.indexOf('['), raw.lastIndexOf(']') + 1));
const P = compile(E);
const texts = JSON.parse(fs.readFileSync(0, 'utf8'));
console.log(JSON.stringify(texts.map(t => [...new Set(match(t, P).map(h => E[h.index].term))])));
"""
out = subprocess.run(["node", "-e", js, str(HERE.parent / "extension/matcher.js"), str(HERE.parent / "extension/data.js")],
                     input=json.dumps([r["text"] for r in rows]), capture_output=True, text=True, check=True)
ext = json.loads(out.stdout)
extra = missing = total_py = total_ext = 0
for row, got in zip(rows, ext):
    ref = {m["term"] for m in search_jargon(row["text"])["matches"]}
    got = set(got)
    total_py += len(ref); total_ext += len(got)
    if got - ref:
        extra += 1; print("多出（不应出现）", row["id"], got - ref)
    for t in ref - got:
        missing += 1
        m = next(m for m in search_jargon(row["text"])["matches"] if m["term"] == t)
        i = row["text"].lower().find(m["matched_text"].lower())
        print("少了", row["id"], t, "| 上下文：", row["text"][max(0, i - 8): i + len(m["matched_text"]) + 4].replace("\n", " "))
print(f"search.py 命中 {total_py}，插件命中 {total_ext}，多出 {extra}，少了 {missing}")
sys.exit(1 if extra else 0)
