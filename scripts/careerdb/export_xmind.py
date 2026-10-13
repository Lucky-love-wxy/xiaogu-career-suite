#!/usr/bin/env python3
"""把职业库（tree/cards/edges/提问树）导出成 XMind 文件 + 同结构 Markdown，给人看全景用。

三个画布：岗位树（只保留有招聘样本的节点及其祖先，无样本的叶子折叠成一个计数节点）、
专业 → 岗位（edges 原样）、医学提问树（草稿）。所有数字都来自库文件，这里不生成新事实。
Markdown 版是兜底：XMind 打不开 .xmind 时可用「文件 → 导入 → Markdown」。
"""
import json
import sys
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "careerdb"
OUT = ROOT / "docs" / "research"
sys.path.insert(0, str(ROOT / "scripts"))
from xmind_dark import upsert_sheets  # noqa: E402
SEP = " › "
STAMP = "2026-10-06"
# 项目唯一的 XMind：所有层级图都以画布形式写进这一个文件（文件名沿用首次导出的名字）
XMIND = OUT / "careerdb-tree-2026-10-06.xmind"


def topic(title, children=None, note=None, folded=False):
    """XMind 2020+ 的 topic 结构；children 为空时不写 children 字段。"""
    t = {"id": uuid.uuid4().hex, "class": "topic", "title": title}
    if children:
        t["children"] = {"attached": children}
    if note:
        t["notes"] = {"plain": {"content": note}}
    if folded and children:
        t["branch"] = "folded"
    return t


def fmt_counts(d, k=5):
    return "、".join(f"{a}{b}" for a, b in sorted(d.items(), key=lambda x: -x[1])[:k])


def card_note(c):
    lines = [f"路径：{c['path']}", f"样本：{c['sample_n']} 份"]
    if c.get("education"):
        lines.append(f"学历：{fmt_counts(c['education'])}")
    if c.get("majors"):
        lines.append(f"专业：{fmt_counts(c['majors'])}")
    if c.get("titles"):
        lines.append("原始岗位名：" + "、".join(c["titles"][:5]))
    for d in c.get("duties", [])[:3]:
        lines.append(f"职责原文：{d}")
    for u in c.get("sample_urls", [])[:2]:
        lines.append(f"样本：{u}")
    return "\n".join(lines)


def build_role_tree(tree, cards, stats):
    """行业 → 类别 → 岗位；只展开有样本的岗位，按样本数排序。"""
    kids = defaultdict(list)
    for path, n in tree.items():
        kids[n.get("parent")].append(path)
    has = {p for p, c in cards.items() if c["sample_n"] > 0}

    def subtotal(path):
        if path in cards:
            return cards[path]["sample_n"]
        return sum(subtotal(k) for k in kids[path])

    def node(path):
        n = tree[path]
        if path in cards:
            c = cards[path]
            mark = "（补充节点）" if c["source"] != "BOSS分类" else ""
            return topic(f"{n['name']} · {c['sample_n']}样本{mark}", note=card_note(c))
        live = sorted((k for k in kids[path] if subtotal(k) > 0), key=lambda k: -subtotal(k))
        empty = [k for k in kids[path] if subtotal(k) == 0]
        ch = [node(k) for k in live]
        if empty:
            ch.append(topic(f"另 {len(empty)} 个岗位无样本",
                            note="、".join(tree[k]["name"] for k in empty)))
        return topic(f"{n['name']} · {subtotal(path)}样本", ch, folded=n["level"] == 2)

    tops = sorted(kids[None], key=lambda k: -subtotal(k))
    branches = [node(k) for k in tops if subtotal(k) > 0]
    zero = [tree[k]["name"] for k in tops if subtotal(k) == 0]
    if zero:
        branches.append(topic(f"另 {len(zero)} 个行业无样本", note="、".join(zero)))
    unm = [topic(f"{name or '（空岗位名）'} · {n}", None) for name, n in stats["unmapped_top"][:20]]
    branches.append(topic(f"未挂上树的样本 {stats['unmapped']} 条（前 20 个岗位名）", unm, folded=True))
    root = topic(f"职业库岗位树（{STAMP}）", [data_note(stats)] + branches)
    root["structureClass"] = "org.xmind.ui.logic.right"
    return {"id": uuid.uuid4().hex, "class": "sheet", "title": "岗位树", "rootTopic": root}, len(has)


def data_note(stats):
    lines = [f"抓取样本 {stats['postings_total']} 条，去重后 {stats['single']} 条",
             f"挂上岗位树 {stats['mapped']} 条，未挂上 {stats['unmapped']} 条",
             f"有样本的岗位节点 {stats['nodes_with_samples']} 个；专业→岗位连线 {stats['edges']} 条",
             "来源：牛企直聘校招单岗页，每个关键词只取搜索第一页",
             "计数是样本数，不是市场岗位数；只有 1 家单位在招的标「证据少」"]
    return topic("数据说明", [topic(s) for s in lines])


def build_major_tree(edges, stats):
    by = defaultdict(list)
    for e in edges:
        by[e["major_class"]].append(e)
    majors = sorted(by, key=lambda m: -sum(e["n"] for e in by[m]))
    branches = []
    for m in majors:
        rows = sorted(by[m], key=lambda e: (-e["company_n"], -e["n"]))
        ch = []
        for e in rows:
            parts = e["node"].split(SEP)
            weak = "，证据少" if e["company_n"] < 2 else ""
            ch.append(topic(f"{parts[-1]}（{parts[0]}）· {e['company_n']}家{weak}",
                            note=f"样本 {e['n']} 份 / {e['company_n']} 家单位\n学历：{fmt_counts(e['education'])}\n"
                                 + "\n".join(e["sample_urls"][:2])))
        total = sum(e["n"] for e in rows)
        branches.append(topic(f"{m} · {len(rows)}个岗位 / {total}样本", ch, folded=True))
    root = topic(f"专业 → 岗位（{STAMP}）", [data_note(stats)] + branches)
    root["structureClass"] = "org.xmind.ui.logic.right"
    return {"id": uuid.uuid4().hex, "class": "sheet", "title": "专业→岗位", "rootTopic": root}


def build_question_tree(q, cards, edges):
    by_name = {}
    for c in cards.values():
        if c["name"] not in by_name or c["sample_n"] > by_name[c["name"]]["sample_n"]:
            by_name[c["name"]] = c
    med = set(q["scope"])
    listed, unknown = set(), []

    def leaf(name):
        listed.add(name)
        c = by_name.get(name)
        if c is None:
            unknown.append(name)
            return topic(f"{name}（库里无此节点）")
        return topic(f"{name} · {c['sample_n']}样本", note=card_note(c))

    def node(n):
        title = f"{n['id']} {n['label']}"
        ch = []
        if n.get("question"):
            ch.append(topic(f"追问：{n['question']}"))
        if isinstance(n.get("leaves"), list):
            ch += [leaf(x) for x in n["leaves"]]
        ch += [node(x) for x in n.get("children", [])]
        return topic(title, ch, note=n.get("what"), folded=True)

    branches = [node(n) for n in q["children"]]
    # C 支 = 医学类专业有连线、但没写进 A/B 的岗位
    c_branch = next(b for b, n in zip(branches, q["children"]) if n["id"] == "C")
    rest = defaultdict(int)
    for e in edges:
        name = e["node"].split(SEP)[-1]
        if e["major_class"] in med and name not in listed:
            rest[name] = max(rest[name], e["company_n"])
    c_branch["children"] = {"attached": [topic(f"{n} · {k}家") for n, k in sorted(rest.items(), key=lambda x: -x[1])]}
    c_branch["branch"] = "folded"
    meta = topic("说明", [topic("草稿 v1，分支划分是设计判断，待确认"),
                          topic("适用专业：" + "、".join(q["scope"])),
                          topic("叶子数字 = 该岗位在全库的样本数")])
    if unknown:
        branches.append(topic("提问树里写了、库里没有的岗位名", [topic(x) for x in sorted(set(unknown))]))
    root = topic(f"医学类提问树：{q['question']}", [meta] + branches)
    root["structureClass"] = "org.xmind.ui.logic.right"
    return {"id": uuid.uuid4().hex, "class": "sheet", "title": "医学提问树", "rootTopic": root}


def to_md(sheets):
    out = []

    def walk(t, depth):
        if depth <= 2:
            out.append(f"{'#' * (depth + 1)} {t['title']}")
        else:
            out.append(f"{'  ' * (depth - 3)}- {t['title']}")
        for c in t.get("children", {}).get("attached", []):
            walk(c, depth + 1)
    for s in sheets:
        walk(s["rootTopic"], 0)
        out.append("")
    return "\n".join(out)


def count(t):
    return 1 + sum(count(c) for c in t.get("children", {}).get("attached", []))


def main():
    tree = json.loads((DB / "tree.json").read_text(encoding="utf-8"))
    cards = json.loads((DB / "cards.json").read_text(encoding="utf-8"))
    edges = json.loads((DB / "edges.json").read_text(encoding="utf-8"))
    stats = json.loads((DB / "stats.json").read_text(encoding="utf-8"))
    q = json.loads((DB / "question_tree_medical.json").read_text(encoding="utf-8"))

    s1, n_has = build_role_tree(tree, cards, stats)
    assert n_has == stats["nodes_with_samples"], (n_has, stats["nodes_with_samples"])
    sheets = [s1, build_major_tree(edges, stats), build_question_tree(q, cards, edges)]

    xmind = XMIND
    upsert_sheets(sheets, xmind, creator="careerdb-export")  # 黑底白线；不动其他脚本写的画布
    (OUT / f"careerdb-tree-{STAMP}.md").write_text(to_md(sheets), encoding="utf-8")
    for s in sheets:
        print(s["title"], count(s["rootTopic"]), "个主题")
    print(xmind)


if __name__ == "__main__":
    main()
