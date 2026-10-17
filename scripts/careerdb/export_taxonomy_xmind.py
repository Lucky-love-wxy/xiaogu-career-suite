#!/usr/bin/env python3
"""把「岗位四级分类 / 连接可能性 / 提问集」三张画布写进项目唯一的 XMind（黑底白线，按标题替换同名画布）。

- 岗位四级分类：data/careerdb/taxonomy_function_v1.json（设计判断）挂上 cards.json 的样本数；
  每个有样本的岗位必须且只能出现一次，否则报错，保证不漏不重。
- 连接可能性：头脑风暴清单写在本文件 LINKS 里，每条标数据现状（已有 / 可计算 / 缺），状态依据是库里的字段。
- 提问集：evals/question-bank 的自拟种子集 + 真实原话，按 阶段 → 类别 → 问题 展开。
"""
import csv
import json
import sys
import uuid
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from xmind_dark import upsert_sheets  # noqa: E402
from export_xmind import XMIND as MASTER  # noqa: E402  项目唯一的 XMind

DB = ROOT / "data" / "careerdb"
QB = ROOT / "evals" / "question-bank"
STAMP = "2026-10-07"


def topic(title, children=None, note=None, folded=False):
    t = {"id": uuid.uuid4().hex, "class": "topic", "title": title}
    if children:
        t["children"] = {"attached": children}
    if note:
        t["notes"] = {"plain": {"content": note}}
    if folded and children:
        t["branch"] = "folded"
    return t


def sheet(title, root):
    root["structureClass"] = "org.xmind.ui.logic.right"
    return {"id": uuid.uuid4().hex, "class": "sheet", "title": title, "rootTopic": root}


# ---------------------------------------------------------------- 1 岗位四级分类

def build_taxonomy(tax, cards):
    by_name = {}
    for c in cards.values():
        if c["sample_n"] > 0:
            assert c["name"] not in by_name, f"岗位名重复：{c['name']}"
            by_name[c["name"]] = c
    seen = []
    mixed = tax["mixed_nodes"]

    def leaf(name):
        c = by_name.get(name)
        assert c is not None, f"分类里写了库里没有的岗位：{name}"
        seen.append(name)
        flag = "（混杂节点）" if name in mixed else ""
        note = f"BOSS 原路径：{c['path']}\n样本 {c['sample_n']} 份"
        if name in mixed:
            note += f"\n混杂原因：{mixed[name]}"
        return topic(f"{name} · {c['sample_n']}{flag}", note=note), c["sample_n"]

    def level(d, depth):
        out, total = [], 0
        for k, v in d.items():
            if isinstance(v, list):
                kids = [leaf(x) for x in v]
                n = sum(x[1] for x in kids)
                out.append((topic(f"{k} · {n}", [x[0] for x in sorted(kids, key=lambda x: -x[1])]), n))
            else:
                kids, n = level(v, depth + 1)
                out.append((topic(f"{k} · {n}", kids, folded=depth >= 1), n))
            total += out[-1][1]
        out.sort(key=lambda x: -x[1])
        return [x[0] for x in out], total

    branches, total = level(tax["tree"], 0)
    dup = {x for x in seen if seen.count(x) > 1}
    missing = set(by_name) - set(seen)
    assert not dup, f"岗位被放进多个小类：{dup}"
    assert not missing, f"有样本但没分类的岗位：{missing}"
    meta = topic("说明", [
        topic("层级：大类 → 中类 → 小类 → 岗位；数字 = 招聘样本数（不是市场岗位数）"),
        topic("按「每天主要做什么」分，不按行业分；BOSS 原路径在每个岗位的备注里"),
        topic(f"覆盖全部 {len(by_name)} 个有样本岗位，共 {total} 条样本；未挂上岗位树的样本不在此图"),
        topic("标「混杂节点」的岗位里混了不同工作，需要再拆", [topic(f"{k}：{v}") for k, v in mixed.items()]),
        topic("v1 草稿：分到哪一类是设计判断，待确认"),
    ])
    return sheet("岗位四级分类", topic(f"岗位四级分类 v1（{STAMP}）", [meta] + branches)), len(by_name)


# ---------------------------------------------------------------- 2 连接可能性

# (分组, 连接, 用户会怎么问, 数据现状, 依据字段)
LINKS = [
    ("人 → 岗位（找方向的入口）", [
        ("专业类 → 岗位", "我学药学能做什么", "已有", "edges.json，892 条，来自招聘原文的需求专业"),
        ("学历 → 岗位门槛", "本科能当临床监查员吗", "已有", "cards.education / postings.edu_level"),
        ("专业 + 学历组合 → 岗位", "护理本科不进医院能去哪", "可计算", "postings 同时有 major_classes 和 edu_level"),
        ("排除某类后的岗位", "学临床不想当医生还能干嘛", "可计算", "专业连线减去「临床医生」中类"),
        ("学校 → 发布单位", "我们学校就业网上都是什么单位", "已有", "postings.source（发布来源多为高校就业网）"),
        ("兴趣 / 性格 → 岗位", "我喜欢跟人打交道适合什么", "缺", "库里没有岗位的工作方式描述，只能靠职责原文推测"),
        ("课程 / 技能 → 岗位", "我会 Python 能投什么", "部分", "esco_skill_pilot.csv 只是试点"),
        ("证书 → 岗位", "没有执业医师证能做什么", "部分", "只能从职责原文里检出，没有结构化字段"),
        ("经历 → 岗位", "我做过家教 能找什么工作", "缺", "无"),
        ("城市 → 岗位", "成都有哪些医药岗", "缺", "postings 没有城市字段"),
        ("薪资期望 → 岗位", "想月薪一万做什么", "缺", "postings 没有薪资字段"),
    ]),
    ("岗位 ↔ 岗位", [
        ("同小类的相近岗位", "临床协调员和临床监查员有什么区别", "已有", "四级分类同一小类"),
        ("跨行业的同类职能", "医药代表和普通销售差在哪", "已有", "四级分类同中类、BOSS 行业不同"),
        ("同专业可达的岗位集合", "药学能做的岗位里哪些不用读博", "可计算", "edges 按专业聚合 + 学历"),
        ("原始岗位名 → 标准岗位", "CRA 是什么岗位", "已有", "cards.titles（原始岗位名）"),
        ("转岗路径", "做了两年 CRC 能转什么", "部分", "onet_transfer_check.csv 只是试点，无国内证据"),
        ("晋升路径", "护士往上能升什么", "缺", "只有护士 → 护士长这类名称线索"),
        ("混杂节点的拆分", "科研岗具体是哪种科研", "缺", "科研岗、临床医生（未细分）等 6 个混杂节点待拆"),
    ]),
    ("岗位 → 环境", [
        ("岗位 → 行业", "这个岗位在哪些行业有", "已有", "BOSS 原路径"),
        ("岗位 → 招聘单位", "哪些单位在招医学编辑", "已有", "postings.company"),
        ("岗位 → 单位类型", "这是医院岗还是企业岗", "可计算", "单位名规则（医院 / 大学 / 有限公司）"),
        ("岗位 → 招聘时间", "这个岗位一般几月招", "已有", "postings.posted"),
        ("岗位 → 地区", "这个岗位哪个城市多", "缺", "无城市字段"),
        ("岗位 → 薪资", "这个岗位刚入行多少钱", "缺", "无薪资字段；只能走实时来源"),
    ]),
    ("岗位 → 内容", [
        ("岗位 → 职责原文", "这个岗位每天干什么", "已有", "cards.duties"),
        ("岗位 → 黑话解释", "JD 里的「抗压」是什么意思", "已有", "database/jargon.json，只在有 JD 时调用"),
        ("岗位 → 从业者说法", "真正做这行的人怎么说", "部分", "practitioner-evidence，仅 7 篇入卡"),
        ("岗位 → 岗位卡", "给我讲讲这个岗位", "部分", "role_cards，多数仍是 jd_only_draft"),
        ("岗位 → 国家标准职业", "这个岗位在职业大典里叫什么", "部分", "node_mapping_standards.csv，provisional，大典编码未取得"),
    ]),
    ("提问 ↔ 岗位", [
        ("提问 → 意图 → 需要哪条连接", "「学护理不进医院能干嘛」= 专业→岗位 + 排除", "可计算", "intent 分类 + 本图连接清单"),
        ("提问 → 医学提问树分支", "「想在医院外用医学知识」→ B 支", "已有", "question_tree_medical.json（仅医学）"),
        ("岗位 → 常见追问", "看完岗位后用户下一句问什么", "缺", "需要真实对话日志（web/logs）积累"),
    ]),
    ("证据质量", [
        ("岗位 → 样本数 / 单位数", "这个说法靠谱吗", "已有", "cards.sample_n、edges.company_n；只有 1 家标「证据少」"),
        ("样本 → 原始链接", "你从哪看到的", "已有", "postings.url"),
        ("岗位 → 证据缺口", "这个岗位哪些信息还不知道", "已有", "research_queue.csv / 审查表「岗位卡缺口」"),
    ]),
]


def build_links():
    status_n = defaultdict(int)
    groups = []
    for g, rows in LINKS:
        kids = []
        for name, q, st, basis in rows:
            status_n[st] += 1
            kids.append(topic(f"[{st}] {name}", [topic(f"例：{q}"), topic(f"依据：{basis}")], folded=True))
        groups.append(topic(g, kids))
    meta = topic("说明", [
        topic("节点类型：专业、学历、学校、单位、行业、岗位、原始岗位名、职责、黑话、从业者说法、提问"),
        topic("已有 = 库里有字段；可计算 = 现有字段组合能算出；部分 = 只有试点或线索；缺 = 需要新数据"),
        topic("统计：" + "、".join(f"{k} {v}" for k, v in status_n.items())),
    ])
    return sheet("连接可能性", topic(f"岗位信息的连接可能性（{STAMP}）", [meta] + groups)), status_n


# ---------------------------------------------------------------- 3 提问集

def build_questions():
    rows = []
    for name, tag in (("seed_brainstorm.csv", "自拟"), ("real_questions.csv", "真实")):
        with (QB / name).open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows.append((tag, r))
    tree = defaultdict(lambda: defaultdict(list))
    for tag, r in rows:
        tree[r["stage"]][r["category"]].append((tag, r))
    branches = []
    for stage, cats in sorted(tree.items(), key=lambda x: -sum(len(v) for v in x[1].values())):
        ckids = []
        for cat, qs in sorted(cats.items(), key=lambda x: -len(x[1])):
            qkids = []
            for tag, r in qs:
                gap = "[缺口] " if r["coverage"] == "N" else ""
                note = (f"来源：{tag}（{r['source']}）\n期望意图：{r['expected_intent']}\n覆盖：{r['coverage']}\n"
                        f"期望行为：{r['expected_behavior']}\n风险：{r['risk']}")
                if tag == "自拟" and r["note"]:
                    note += f"\n要点：{r['note']}"
                qkids.append(topic(f"{gap}[{tag}] {r['question']}", note=note))
            ckids.append(topic(f"{cat} · {len(qs)}", qkids, folded=True))
        n = sum(len(v) for v in cats.values())
        branches.append(topic(f"{stage} · {n}", ckids, folded=True))
    n_seed = sum(1 for t, _ in rows if t == "自拟")
    meta = topic("说明", [
        topic(f"自拟 {n_seed} 条（Claude 头脑风暴，只代表猜测）；真实 {len(rows) - n_seed} 条（Codex 采集，偏豆瓣旧帖）"),
        topic("[缺口] = 现有 9 类意图都接不住"),
        topic("每条备注里有期望意图、期望行为、风险"),
    ])
    return sheet("提问集", topic(f"小谷提问集（{STAMP}）", [meta] + branches)), len(rows)


def main():
    tax = json.loads((DB / "taxonomy_function_v1.json").read_text(encoding="utf-8"))
    cards = json.loads((DB / "cards.json").read_text(encoding="utf-8"))
    s1, n_roles = build_taxonomy(tax, cards)
    s2, status_n = build_links()
    s3, n_q = build_questions()
    titles = upsert_sheets([s1, s2, s3], MASTER)
    print(f"岗位四级分类：{n_roles} 个岗位；连接：{dict(status_n)}；提问：{n_q} 条")
    print(MASTER, "画布：", "、".join(titles))


if __name__ == "__main__":
    main()
