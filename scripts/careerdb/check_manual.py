#!/usr/bin/env python3
"""验收：人工逐份核实的招聘说明，脚本归到的岗位节点必须与人工判断一致。"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {"医学编辑": "医学编辑", "临床研究协调员（CRC）": "临床协调员", "药物警戒专员": "药物警戒", "药物警戒校招实习": "药物警戒",
            "医学信息沟通专员（医药代表）": "医药代表", "医学理赔": "医学理赔/核保", "药品注册专员": "药品注册", "医学运营专员": "医学运营",
            "运营管理岗": "医疗机构运营管理", "运营管理管培生": "医疗机构运营管理", "学术编辑": "期刊/学术编辑",
            "英文医学期刊编辑": "期刊/学术编辑", "期刊编辑/编务": "期刊/学术编辑",
            "生物医学大模型研发": "医学AI/生物医学大模型"}
rows = [json.loads(l) for l in (ROOT / "data/careerdb/postings_mapped.jsonl").read_text(encoding="utf-8").split("\n") if l.strip()]
bad = [(r["role"], (r["node"] or "未归类").split(" › ")[-1]) for r in rows if r.get("manual")
       and (r["node"] or "").split(" › ")[-1] != EXPECTED.get(r["role"])]
total = sum(1 for r in rows if r.get("manual"))
print(f"人工样本归类一致 {total - len(bad)}/{total}")
for role, got in bad:
    print("  不一致：", role, "→", got, "，期望", EXPECTED.get(role))
sys.exit(1 if bad else 0)
