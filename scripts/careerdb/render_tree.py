#!/usr/bin/env python3
"""把提问树（question_tree_medical.json）按专业剪枝，并挂上库里的证据，生成给人审阅的文档。

每个专业只保留它在 edges.json 里有连线的岗位；没有岗位的分支整支隐藏。岗位的门槛计数、职责原句都来自
cards/edges（招聘原文），这里不生成任何新事实。提问树里写了但库里不存在的岗位名会列在文末，便于修正。
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "careerdb"
SEP = " › "


def main() -> None:
    tree = json.loads((DB / "question_tree_medical.json").read_text(encoding="utf-8"))
    cards = json.loads((DB / "cards.json").read_text(encoding="utf-8"))
    edges = json.loads((DB / "edges.json").read_text(encoding="utf-8"))
    by_name = defaultdict(list)
    for path, c in cards.items():
        by_name[c["name"]].append(path)
    listed, unknown = set(), []

    def walk(node):
        if isinstance(node.get("leaves"), list):
            for n in node["leaves"]:
                listed.add(n)
                if n not in by_name:
                    unknown.append(n)
        for ch in node.get("children", []):
            walk(ch)
    walk(tree)

    edge_by = defaultdict(dict)  # 专业类 → {岗位名: 连线}（同名岗位跨大类时合并到样本多的那条）
    for e in edges:
        name = e["node"].split(SEP)[-1]
        old = edge_by[e["major_class"]].get(name)
        if old is None or e["n"] > old["n"]:
            edge_by[e["major_class"]][name] = e

    def leaf_line(name: str, e: dict) -> str:
        card = cards.get(e["node"], {})
        edu = "、".join(f"{k}{v}" for k, v in e["education"].items())
        strength = "" if e["company_n"] >= 2 else "，证据少"
        duties = "；".join(f"“{d}”" for d in card.get("duties", [])[:2])
        return (f"  - {name}：{e['n']} 份样本 / {e['company_n']} 家单位{strength}（学历：{edu}）"
                + (f"\n    - 招聘原文职责：{duties}" if duties else "")
                + f"\n    - 搜索词：{name.split('（')[0].split('/')[0]} 应届")

    out = ["# 医学类提问树（草稿 v1，自动生成）", "",
           "- 树结构：data/careerdb/question_tree_medical.json（分支划分是设计判断，待确认）；证据：data/careerdb/cards.json、edges.json。",
           "- 每个专业只显示有招聘连线的岗位。“证据少”= 只有 1 家单位在招，不说门槛结论。", "",
           f"第一问：{tree['question']}", ""]
    for major in tree["scope"]:
        have = edge_by.get(major, {})
        if not have:
            out += [f"## {major}", "", "本次没有连线样本。", ""]
            continue
        out += [f"## {major}（{len(have)} 个岗位有样本）", ""]
        for top in tree["children"]:
            if top["id"] == "C":
                rest = [n for n in have if n not in listed]
                if rest:
                    out.append(f"- **{top['id']} {top['label']}**：{top['what']}")
                    out.append("  - " + "；".join(f"{n} {have[n]['company_n']}家" for n in sorted(rest, key=lambda n: -have[n]["company_n"])))
                continue
            groups = top.get("children") or [top]
            blocks = []
            for g in groups:
                rows = [n for n in g["leaves"] if n in have]
                if rows:
                    head = f"- **{g['id']} {g['label']}**：{g['what']}" if g is not top else ""
                    blocks.append((head, sorted(rows, key=lambda n: -have[n]["company_n"])))
            if not blocks:
                continue
            out.append(f"### {top['id']} {top['label']}")
            out.append(top["what"])
            if top.get("question"):
                out.append(f"追问：{top['question']}")
            out.append("")
            for head, rows in blocks:
                if head:
                    out.append(head)
                out += [leaf_line(n, have[n]) for n in rows]
            out.append("")
    out += ["## 提问树里写了、库里没有的岗位名（需要修正树或补节点）", "", "、".join(sorted(set(unknown))) or "无", ""]
    (ROOT / "docs" / "research" / "question-tree-medical-v1.md").write_text("\n".join(out), encoding="utf-8")
    print(f"岗位名未在库中：{sorted(set(unknown))}")


if __name__ == "__main__":
    main()
