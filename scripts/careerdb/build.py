#!/usr/bin/env python3
"""职业库 v2 构建：岗位树（BOSS 分类 + 招聘样本补充节点）+ 专业→岗位连线 + 岗位卡片 + 给人看的全景报告。

全部由 evidence 与 data/careerdb/postings.jsonl 离线生成，不联网、不调用模型。
v1 原则（用户 2026-10-05）：尽可能广、不出错——岗位名尽量多列；门槛只按样本计数，不写“通常”。
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TREE_SRC = ROOT / "evidence" / "careerdb-2026-10-05" / "boss-position-tree.json"
POSTINGS = ROOT / "data" / "careerdb" / "postings.jsonl"
# 人工逐份核实过的招聘说明（Codex 6 份 + Claude 21 份，2026-10-05），并入样本并单独计数
MANUAL = [ROOT / "data" / "directions" / "role_postings.csv", ROOT / "data" / "directions" / "role_postings_2026-10-05_claude.csv"]
OUT = ROOT / "data" / "careerdb"
REPORT = ROOT / "docs" / "research"
SEP = " › "  # 路径分隔符；BOSS 名称里本身含“/”，不能用“/”

# 专业类：按教育部本科专业目录的专业类名称整理（未逐项核对目录原文）；值是页面上可能出现的写法，含缩写和牛企直聘的拼音代码
MAJOR_CLASSES = {
    "基础医学类": ["基础医学", "jichuyixue"],
    "临床医学类": ["临床医学", "临床", "linchuang", "内科学", "外科学", "儿科学", "妇产科学", "急诊医学", "重症医学", "麻醉学",
                "医学影像学", "眼视光医学", "精神医学", "放射医学", "眼科学", "全科医学", "神经病学", "肿瘤学", "皮肤病与性病学",
                "耳鼻咽喉科学", "急诊", "重症", "影像医学与核医学", "精神病与精神卫生"],
    "口腔医学类": ["口腔医学", "口腔", "kouqiang"],
    "公共卫生与预防医学类": ["预防医学", "公共卫生", "公卫", "流行病与卫生统计学", "卫生检验与检疫", "食品卫生与营养学", "妇幼保健医学", "yufangyixue"],
    "中医学类": ["中医学", "针灸推拿学", "中医", "中西医临床医学", "中西医结合", "zhongyixue"],
    "药学类": ["药学", "临床药学", "药物制剂", "药物分析", "药物化学", "药理学", "药事管理", "yaoxue"],
    "中药学类": ["中药学", "中药资源与开发", "中药制药"],
    "法医学类": ["法医学"],
    "医学技术类": ["医学检验技术", "医学检验", "医学影像技术", "康复治疗学", "康复治疗", "眼视光学", "口腔医学技术", "卫生检验",
                "听力与言语康复学", "医学实验技术", "医学技术", "yixuejishu"],
    "护理学类": ["护理学", "护理", "助产学", "助产", "huli"],
    "生物医学工程类": ["生物医学工程"],
    "生物科学类": ["生物科学", "生物技术", "生物信息学", "生物学", "生物"],
    "化学类": ["化学"],
    "心理学类": ["心理学", "应用心理学"],
    "公共管理类": ["卫生事业管理", "劳动与社会保障", "公共事业管理", "健康服务与管理", "医疗保险"],
    "金融学类": ["保险学", "金融学", "精算学"],
    "法学类": ["法学"],
    "中国语言文学类": ["汉语言文学", "中文"],
    "新闻传播学类": ["新闻学", "传播学", "新闻传播"],
    "外国语言文学类": ["英语", "日语", "翻译"],
    "计算机类": ["计算机", "软件工程", "人工智能", "数据科学"],
    "统计学类": ["统计学", "生物统计"],
    "工商管理类": ["工商管理", "市场营销", "人力资源管理", "会计学", "财务管理"],
}
MEDICAL = ["基础医学类", "临床医学类", "口腔医学类", "公共卫生与预防医学类", "中医学类", "药学类", "中药学类",
           "法医学类", "医学技术类", "护理学类"]

# 招聘样本里常见、但 BOSS 分类没有单列的岗位：补充节点，挂在最贴近的 BOSS 中类下，来源标“招聘样本”
SUPPLEMENT = [
    ("药物警戒", ("医疗健康", "生物医药"), ["药物警戒", "药品警戒", "PV专员", "药物安全"]),
    ("医学事务/医学信息", ("医疗健康", "临床试验"), ["医学事务", "医学联络", "MSL", "医学信息专员", "医学专员"]),
    ("医学写作", ("医疗健康", "临床试验"), ["医学写作", "Medical Writ"]),
    ("医学理赔/核保", ("金融", "保险"), ["医学理赔", "医疗理赔", "医疗核保", "医学核保", "核保", "人伤理赔", "理赔"]),
    ("医学运营", ("客服/运营", "业务运营"), ["医学运营", "医疗运营", "医务运营"]),
    ("医学内容审核", ("客服/运营", "业务运营"), ["医学内容审核", "医疗内容审核", "医学审核"]),
    ("临床医生（科室未细分）", ("医疗健康", "医生/医技"), ["临床医师", "临床医生", "住院医师", "医师", "医生"]),
    ("公共卫生/疾控", ("医疗健康", "其他医疗健康职位"), ["疾控", "疾病预防控制", "公共卫生", "卫生监督", "传染病防控"]),
    ("医保/医院管理", ("医疗健康", "医生/医技"), ["医保", "医务科", "病案", "医院管理", "质控"]),
    ("医学教育/题库", ("教育培训", "教育产品研发"), ["医学教研", "题库", "医学讲师", "医学教育"]),
    ("期刊/学术编辑", ("影视/传媒", "采编/写作/出版"), ["期刊编辑", "学术编辑", "编务"]),
    ("医疗机构运营管理", ("医疗健康", "其他医疗健康职位"), ["运营管理", "医疗管理", "医疗运营管理"]),
]


def load_tree() -> tuple[dict, list]:
    """返回 nodes（path → 节点）与可匹配的末级列表 [(name, path)]。"""
    top = json.loads(TREE_SRC.read_text(encoding="utf-8"))["zpData"]["position"]
    nodes, leaves = {}, []
    for a in top:
        nodes[a["name"]] = {"name": a["name"], "level": 1, "source": "BOSS分类", "code": a["code"]}
        for b in a.get("subLevelModelList") or []:
            pb = f"{a['name']}{SEP}{b['name']}"
            nodes[pb] = {"name": b["name"], "level": 2, "source": "BOSS分类", "code": b["code"], "parent": a["name"]}
            for c in b.get("subLevelModelList") or []:
                pc = f"{pb}{SEP}{c['name']}"
                nodes[pc] = {"name": c["name"], "level": 3, "source": "BOSS分类", "code": c["code"], "parent": pb}
                leaves.append((c["name"], pc))
    for name, parent, _ in SUPPLEMENT:
        path = SEP.join(parent + (name,))
        nodes[path] = {"name": name, "level": 3, "source": "招聘样本补充", "parent": SEP.join(parent)}
    return nodes, leaves


ROLE_NOISE = re.compile(r"[（(【\[].*?[)）】\]]|J\d+|20\d\d届?|校招|校园招聘|应届生?|实习生?|管培生|储备|招聘|岗位?$")


def leaf_alts(name: str) -> list:
    """“人力资源专员/助理”→[人力资源专员, 人力资源助理]；“营养师/健康管理师”→两个全称。短后缀不单独用，避免“助理”误配一切。"""
    parts = name.split("/")
    base, out = parts[0], [parts[0]]
    for p in parts[1:]:
        out.append(base[:-len(p)] + p if len(p) <= 2 and len(base) > len(p) else p)
    return [x for x in out if len(x) >= 2]


# 常见写法 → 已有节点（BOSS 末级或补充节点），在 BOSS 名称匹配之后、“医生”兜底之前使用
ALIASES = [
    (["护理", "护士"], ("医疗健康", "护士/护理", "护士")),
    (["临床医学"], ("医疗健康", "医生/医技", "临床医生（科室未细分）")),
    (["医学检验", "检验技师", "检验科"], ("医疗健康", "医生/医技", "医学检验")),
    (["药师", "药剂"], ("医疗健康", "医生/医技", "药剂师")),
    (["康复"], ("医疗健康", "理疗保健", "康复治疗师")),
    (["临床研究协调", "临床协调", "研究协调员"], ("医疗健康", "临床试验", "临床协调员")),
    (["临床监查", "监查员"], ("医疗健康", "临床试验", "临床监查员")),
    (["医学信息沟通", "医药信息沟通", "医药代表", "学术专员"], ("医疗健康", "医疗销售", "医药代表")),
]


def map_role(role: str, leaves: list) -> tuple[str | None, str]:
    """岗位名 → 树节点。先查补充节点的关键词（更具体），再查 BOSS 末级名称包含关系；都不中返回 None。"""
    r = ROLE_NOISE.sub("", role or "").strip()
    generic = [x for x in SUPPLEMENT if x[0].startswith("临床医生")]
    for name, parent, keys in [x for x in SUPPLEMENT if x not in generic]:  # 先匹配具体补充节点
        if any(k.lower() in r.lower() for k in keys):
            return SEP.join(parent + (name,)), "关键词"
    best = None
    for name, path in leaves:
        # 只认“分类名出现在岗位名里”；名称带“/”的拆成几个别名。反向包含（岗位名是分类名的一部分）误配太多，不用
        alts = leaf_alts(name)
        if any(x in r for x in alts):
            if best is None or len(name) > len(best[0]):
                best = (name, path)
    if best:
        return best[1], "BOSS末级名称"
    for keys, path in ALIASES:
        if any(k in r for k in keys):
            return SEP.join(path), "别名"
    for name, parent, keys in generic:  # 最后才用“医生/医师”这类泛称兜底
        if any(k in r for k in keys):
            return SEP.join(parent + (name,)), "关键词"
    return None, "未归类"


def major_classes(rec: dict) -> tuple[list, str]:
    raw = rec.get("majors_raw") or ""
    if re.search(r"不限", raw):
        return ["不限专业"], "需求专业字段"
    found = [c for c, names in MAJOR_CLASSES.items() if any(n.lower() in raw.lower() for n in names)]
    if found:
        return found, "需求专业字段"
    # 字段缺失时，只从职责原文里找完整专业名（≥3 字），避免“临床”“生物”这类短词误配
    desc = rec.get("description") or ""
    found = [c for c, names in MAJOR_CLASSES.items() if any(len(n) >= 3 and n in desc for n in names)]
    return found, ("职责原文" if found else "未写")


def edu_level(s: str | None) -> str:
    s = s or ""
    for k, v in (("博士", "博士"), ("硕士", "硕士"), ("研究生", "硕士"), ("本科", "本科"), ("大专", "大专"), ("专科", "大专")):
        if k in s:
            return v
    return "未写"


def duty_lines(desc: str) -> list:
    """职责原句：取“职责”段里 6–30 字的短句，逐字来自原文。"""
    part = re.split(r"任职(?:要求|资格)|岗位要求|职位要求", desc)[0]
    out = []
    for line in re.split(r"[\n；;。]", part):
        line = re.sub(r"^\s*[\d一二三四五六七八九十]+[、.．)）]\s*", "", line).strip()
        if 6 <= len(line) <= 30 and not re.search(r"职责|发布|薪资|地点|时间|人数", line):
            out.append(line)
    return out[:3]


def load_manual() -> list:
    import csv
    out = []
    for f in MANUAL:
        if not f.exists():
            continue
        for i, row in enumerate(csv.DictReader(f.open(encoding="utf-8")), 1):
            out.append({"id": f"manual-{f.stem}-{i}", "url": row["url"], "kind": "single", "manual": True,
                        "company": row.get("company") or row.get("company_type"), "role": row["role_name"],
                        "majors_raw": row.get("major_req"), "education": row.get("education_req"),
                        "experience": row.get("experience_req"), "description": "", "posted": row.get("posted_or_seen_at"),
                        "archived": False, "source": row.get("platform")})
    return out


def main() -> None:
    nodes, leaves = load_tree()
    recs = [json.loads(l) for l in POSTINGS.read_text(encoding="utf-8").splitlines() if l.strip()]
    singles = [r for r in recs if r["kind"] == "single"] + load_manual()
    cards = defaultdict(lambda: {"samples": [], "edu": Counter(), "majors": Counter(), "duties": [], "titles": Counter(), "manual": 0})
    edges = defaultdict(lambda: {"n": 0, "edu": Counter(), "ids": []})
    unmapped = Counter()
    for r in singles:
        path, how = map_role(r["role"], leaves)
        classes, msrc = major_classes(r)
        edu = edu_level(r.get("education"))
        r.update(node=path, node_match=how, major_classes=classes, major_source=msrc, edu_level=edu)
        if not path:
            unmapped[ROLE_NOISE.sub("", r["role"]).strip()] += 1
            continue
        c = cards[path]
        c["samples"].append(r["url"]); c["manual"] += bool(r.get("manual")); c["edu"][edu] += 1; c["titles"][r["role"]] += 1
        for m in classes:
            c["majors"][m] += 1
            e = edges[(m, path)]; e["n"] += 1; e["edu"][edu] += 1; e["ids"].append(r["url"])
        for d in duty_lines(r.get("description") or ""):
            if d not in c["duties"] and len(c["duties"]) < 5:
                c["duties"].append(d)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tree.json").write_text(json.dumps(nodes, ensure_ascii=False, indent=1), encoding="utf-8")
    card_out = {}
    for path, n in nodes.items():
        if n["level"] != 3:
            continue
        c = cards.get(path)
        card_out[path] = {
            "name": n["name"], "path": path, "source": n["source"],
            "evidence_level": "有招聘样本" if c else "仅分类名称",
            "sample_n": len(c["samples"]) if c else 0,
            "education": dict(c["edu"]) if c else {},
            "majors": dict(c["majors"].most_common()) if c else {},
            "titles": [t for t, _ in c["titles"].most_common(5)] if c else [],
            "duties": c["duties"] if c else [],
            "manual_verified_n": c["manual"] if c else 0,
            "sample_urls": c["samples"][:5] if c else [],
        }
    (OUT / "cards.json").write_text(json.dumps(card_out, ensure_ascii=False, indent=1), encoding="utf-8")
    edge_out = [{"major_class": m, "node": p, "n": e["n"], "education": dict(e["edu"]),
                 "sample_urls": e["ids"][:5]}
                for (m, p), e in sorted(edges.items(), key=lambda kv: -kv[1]["n"])]
    (OUT / "edges.json").write_text(json.dumps(edge_out, ensure_ascii=False, indent=1), encoding="utf-8")
    with (OUT / "postings_mapped.jsonl").open("w", encoding="utf-8") as f:
        for r in singles:
            f.write(json.dumps({k: r.get(k) for k in ("id", "url", "company", "role", "node", "node_match", "major_classes",
                                                         "major_source", "edu_level", "posted", "archived", "source", "manual")},
                               ensure_ascii=False) + "\n")
    stats = {"postings_total": len(recs), "single": len(singles), "mapped": len(singles) - sum(unmapped.values()),
             "unmapped": sum(unmapped.values()), "nodes_with_samples": len(cards), "edges": len(edge_out),
             "boss_leaves": len(leaves), "supplement_nodes": len(SUPPLEMENT)}
    (OUT / "stats.json").write_text(json.dumps({**stats, "unmapped_top": unmapped.most_common(40)}, ensure_ascii=False, indent=1), encoding="utf-8")
    write_report(card_out, edge_out, stats, unmapped)
    print(json.dumps(stats, ensure_ascii=False))


def write_report(cards: dict, edges: list, stats: dict, unmapped: Counter) -> None:
    """给人看的医学全景：每个医学专业类 → 大类 → 中类 → 岗位（样本数、学历分布）。"""
    lines = ["# 医学类专业 → 岗位全景（职业库 v2，自动生成）", "",
             "- 生成：scripts/careerdb/build.py；数据：牛企直聘校招单岗页（站内搜索第一页，2026-10-05 抓取）+ BOSS 职位分类树",
             "- 计数是本次抓到的校招样本数，不是全国岗位数；学历是样本页面写的最低要求。",
             f"- 样本 {stats['single']} 条，挂上岗位树 {stats['mapped']} 条，未归类 {stats['unmapped']} 条；有样本的岗位节点 {stats['nodes_with_samples']} 个。", ""]
    by_major = defaultdict(list)
    for e in edges:
        by_major[e["major_class"]].append(e)
    for m in MEDICAL + ["不限专业"]:
        es = by_major.get(m, [])
        lines.append(f"## {m}（{len(es)} 个岗位，{sum(e['n'] for e in es)} 条样本）")
        if not es:
            lines += ["", "本次没有样本。", ""]
            continue
        tree = defaultdict(lambda: defaultdict(list))
        for e in es:
            a, b, c = e["node"].split(SEP)
            tree[a][b].append(e)
        for a, mids in sorted(tree.items(), key=lambda kv: -sum(x["n"] for v in kv[1].values() for x in v)):
            lines.append(f"- **{a}**")
            for b, es2 in sorted(mids.items(), key=lambda kv: -sum(x["n"] for x in kv[1])):
                items = "；".join(f"{e['node'].split(SEP)[-1]} {e['n']}（{'、'.join(f'{k}{v}' for k, v in e['education'].items())}）"
                                 for e in sorted(es2, key=lambda x: -x["n"]))
                lines.append(f"  - {b}：{items}")
        lines.append("")
    lines += ["## 未归类岗位名（高频，待补充节点）", "", "、".join(f"{k}×{v}" for k, v in unmapped.most_common(40)), ""]
    (REPORT / "careerdb-medical-v1.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
