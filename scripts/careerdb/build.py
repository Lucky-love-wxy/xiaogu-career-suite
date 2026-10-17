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
    "生物科学类": ["生物科学", "生物技术", "生物信息学", "生物学"],
    "生物工程类": ["生物工程", "生物制药"],
    "化学类": ["应用化学", "化学"],
    "化工与制药类": ["化学工程与工艺", "化学工程", "制药工程", "化工"],
    "心理学类": ["心理学", "应用心理学"],
    "公共管理类": ["卫生事业管理", "劳动与社会保障", "公共事业管理", "健康服务与管理", "医疗保险", "行政管理", "土地资源管理"],
    "金融学类": ["保险学", "金融学", "金融工程", "投资学", "精算学", "金融"],
    "经济学类": ["经济学", "国民经济管理", "数字经济"],
    "财政学类": ["财政学", "税收学", "税务"],
    "经济与贸易类": ["国际经济与贸易", "国际贸易", "贸易经济"],
    "法学类": ["法学", "知识产权", "法律"],
    "社会学类": ["社会学", "社会工作"],
    "政治学类": ["政治学与行政学", "国际政治"],
    "马克思主义理论类": ["思想政治教育"],
    "中国语言文学类": ["汉语言文学", "汉语国际教育", "汉语言", "中文", "秘书学"],
    "新闻传播学类": ["新闻学", "传播学", "广告学", "网络与新媒体", "编辑出版学", "新闻传播"],
    "外国语言文学类": ["英语", "日语", "翻译", "商务英语", "俄语", "法语", "德语", "西班牙语", "朝鲜语", "外语"],
    "历史学类": ["历史学"],
    "哲学类": ["哲学"],
    "教育学类": ["教育学", "学前教育", "小学教育", "教育技术学", "特殊教育"],
    "体育学类": ["体育教育", "社会体育指导与管理", "运动训练", "体育"],
    "计算机类": ["计算机科学与技术", "计算机", "软件工程", "人工智能", "数据科学与大数据技术", "网络工程", "信息安全", "物联网工程", "大数据"],
    "电子信息类": ["电子信息工程", "通信工程", "电子科学与技术", "微电子", "集成电路", "光电信息"],
    "自动化类": ["自动化"],
    "电气类": ["电气工程及其自动化", "电气工程", "电气"],
    "机械类": ["机械设计制造及其自动化", "机械电子工程", "机械工程", "车辆工程", "机械"],
    "材料类": ["材料科学与工程", "材料"],
    "土木类": ["土木工程", "给排水", "建筑环境与能源应用"],
    "建筑类": ["建筑学", "城乡规划", "风景园林"],
    "管理科学与工程类": ["工程管理", "工程造价", "信息管理与信息系统", "管理科学"],
    "环境科学与工程类": ["环境工程", "环境科学"],
    "能源动力类": ["能源与动力工程", "新能源"],
    "测绘类": ["测绘工程", "遥感"],
    "交通运输类": ["交通运输", "交通工程"],
    "物流管理与工程类": ["物流管理", "物流工程", "供应链"],
    "数学类": ["数学与应用数学", "信息与计算科学", "数学"],
    "统计学类": ["应用统计学", "统计学", "生物统计"],
    "物理学类": ["物理学", "应用物理"],
    "食品科学与工程类": ["食品科学与工程", "食品质量与安全", "食品"],
    "植物生产类": ["农学", "园艺", "植物保护"],
    "动物医学类": ["动物医学", "兽医"],
    "林学类": ["林学"],
    "工商管理类": ["工商管理", "市场营销", "人力资源管理", "会计学", "会计", "财务管理", "审计学", "审计", "资产评估"],
    "电子商务类": ["电子商务"],
    "旅游管理类": ["旅游管理", "酒店管理", "会展经济"],
    "设计学类": ["视觉传达设计", "环境设计", "产品设计", "数字媒体艺术", "服装设计", "设计"],
    "美术学类": ["美术学", "绘画"],
    "戏剧与影视学类": ["动画", "播音与主持艺术", "广播电视编导", "戏剧影视文学", "影视"],
    "音乐与舞蹈学类": ["音乐学", "音乐", "舞蹈"],
    "地理科学类": ["地理科学", "地理信息科学", "人文地理"],
    "海洋科学类": ["海洋科学"],
}
MEDICAL = ["基础医学类", "临床医学类", "口腔医学类", "公共卫生与预防医学类", "中医学类", "药学类", "中药学类",
           "法医学类", "医学技术类", "护理学类"]

# 招聘样本里常见、但 BOSS 分类没有单列的岗位：补充节点，挂在最贴近的 BOSS 中类下，来源标“招聘样本”
SUPPLEMENT = [
    ("药物警戒", ("医疗健康", "生物医药"), ["药物警戒", "药品警戒", "PV专员", "药物安全"]),
    ("医学事务/医学信息", ("医疗健康", "临床试验"), ["医学事务", "医学联络", "MSL", "医学信息专员", "医学专员", "真实世界研究"]),
    ("医学写作", ("医疗健康", "临床试验"), ["医学写作", "Medical Writ"]),
    ("医学理赔/核保", ("金融", "保险"), ["医学理赔", "医疗理赔", "医疗核保", "医学核保", "人伤理赔", "理赔作业"]),
    ("医学运营", ("客服/运营", "业务运营"), ["医学运营", "医疗运营", "医务运营"]),
    ("医学内容审核", ("客服/运营", "业务运营"), ["医学内容审核", "医疗内容审核", "医学审核"]),
    ("临床医生（科室未细分）", ("医疗健康", "医生/医技"), ["临床医师", "临床医生", "住院医师", "医师", "医生"]),
    ("公共卫生/疾控", ("医疗健康", "其他医疗健康职位"), ["疾控", "疾病预防控制", "公共卫生", "卫生监督", "传染病防控"]),
    ("医保/医院管理", ("医疗健康", "医生/医技"), ["医保", "医务科", "病案", "医院管理"]),
    ("医学教育/题库", ("教育培训", "教育产品研发"), ["医学教研", "题库", "医学讲师", "医学教育"]),
    ("期刊/学术编辑", ("影视/传媒", "采编/写作/出版"), ["期刊编辑", "学术编辑", "编务"]),
    ("科研岗（博士后/研究助理）", ("医疗健康", "生物医药"), ["博士后", "教学科研", "研究助理", "科研助理", "科研人员"]),
    ("医学技师（影像/放疗/导管等）", ("医疗健康", "医生/医技"), ["技师", "放疗", "影像技术"]),
    ("软件开发工程师（未细分）", ("互联网/AI", "后端开发"), ["软件工程师", "软件开发", "程序员"]),
    ("人工智能工程师（未细分）", ("互联网/AI", "人工智能"), ["人工智能工程师", "AI工程师", "人工智能研发"]),
    ("信息安全工程师", ("互联网/AI", "运维/技术支持"), ["信息安全"]),
    ("管理培训生", ("高级管理", "高级管理职位"), ["管理培训", "管培"]),
    ("高校教师/辅导员", ("教育培训", "教师"), ["教授", "高校教师", "专任教师", "辅导员", "专职教师"]),
    ("实验室/检测技术员", ("生产制造", "质量管理"), ["实验技术员", "化学分析", "检测技术员", "实验员", "分析技术员", "检验员", "实验室运营"]),
    ("医学AI/生物医学大模型", ("互联网/AI", "人工智能"), ["医学大模型", "生物医学大模型", "医疗AI", "AI医疗", "AI医学", "医学人工智能", "医疗大模型", "AI制药", "AI药物", "AIDD", "AI化学", "制药知识AI", "AI for Science", "医学影像算法", "虚拟细胞"]),
    ("临床数据管理/生物统计", ("医疗健康", "临床试验"), ["临床数据管理", "临床数据管理员", "生物统计", "统计程序员", "SAS程序员"]),
    ("医药市场（产品/品牌）", ("医疗健康", "医疗销售"), ["医药市场", "医学市场", "医药品牌", "医药产品专员"]),
    ("医疗机构运营管理", ("医疗健康", "其他医疗健康职位"), ["运营管理", "医疗管理", "医疗运营管理"]),
]


def load_tree() -> tuple[dict, list]:
    """返回 nodes（path → 节点）与可匹配的末级列表 [(name, path)]。"""
    top = json.loads(TREE_SRC.read_text(encoding="utf-8"))["zpData"]["position"]
    nodes, leaves, seen = {}, [], set()
    top = sorted(top, key=lambda a: a["name"] != "医疗健康")  # 同名岗位（医药代表、康复治疗师）优先挂医疗健康
    for a in top:
        nodes[a["name"]] = {"name": a["name"], "level": 1, "source": "BOSS分类", "code": a["code"]}
        for b in a.get("subLevelModelList") or []:
            pb = f"{a['name']}{SEP}{b['name']}"
            nodes[pb] = {"name": b["name"], "level": 2, "source": "BOSS分类", "code": b["code"], "parent": a["name"]}
            for c in b.get("subLevelModelList") or []:
                pc = f"{pb}{SEP}{c['name']}"
                nodes[pc] = {"name": c["name"], "level": 3, "source": "BOSS分类", "code": c["code"], "parent": pb}
                if c["name"] not in seen:
                    seen.add(c["name"])
                    leaves.append((c["name"], pc))
    for name, parent, _ in SUPPLEMENT:
        path = SEP.join(parent + (name,))
        nodes[path] = {"name": name, "level": 3, "source": "招聘样本补充", "parent": SEP.join(parent)}
    return nodes, leaves


ROLE_NOISE = re.compile(r"^[^-—]{1,12}分公司[-—]|[（(【\[].*?[)）】\]]|J\d+|20\d\d届?|校招|校园招聘|应届生?|实习生?|管培生|储备|招聘|岗位?$")


def leaf_alts(name: str) -> list:
    """“人力资源专员/助理”→[人力资源专员, 人力资源助理]；“营养师/健康管理师”→两个全称。短后缀不单独用，避免“助理”误配一切。"""
    parts = name.split("/")
    base, out = parts[0], [parts[0]]
    for p in parts[1:]:
        out.append(base[:-len(p)] + p if len(p) <= 2 and len(base) > len(p) else p)
    if name.endswith("医生") and len(name) >= 5:
        out.append(name[:-2])
    return [x for x in out if len(x) >= 2]


# 含义明确的短词，出现在岗位名任何位置都算，且先于 BOSS 名称匹配（否则“核保数据管培生”会挂到“数据”）
PRE_ALIASES = [
    (["理赔", "核保", "核赔"], ("金融", "保险", "保险理赔")),
]

# 常见写法 → 已有节点（BOSS 末级或补充节点），在 BOSS 名称匹配之后、“医生”兜底之前使用
ALIASES = [
    (["护理", "护士"], ("医疗健康", "护士/护理", "护士")),
    (["临床医学"], ("医疗健康", "医生/医技", "临床医生（科室未细分）")),
    (["医学检验", "检验技师", "检验科"], ("医疗健康", "医生/医技", "医学检验")),
    (["药师", "药剂"], ("医疗健康", "医生/医技", "药剂师")),
    (["康复治疗"], ("医疗健康", "理疗保健", "康复治疗师")),
    (["规培", "住院医生", "规范化培训"], ("医疗健康", "医生/医技", "临床医生（科室未细分）")),
    (["临床研究协调", "临床协调", "研究协调员"], ("医疗健康", "临床试验", "临床协调员")),
    (["临床监查", "监查员"], ("医疗健康", "临床试验", "临床监查员")),
    (["医学信息沟通", "医药信息沟通", "医药代表", "学术专员"], ("医疗健康", "医疗销售", "医药代表")),
    (["照护师", "护理员"], ("医疗健康", "护士/护理", "护工")),
    (["医疗助理"], ("医疗健康", "医生/医技", "医生助理")),
    (["制剂研究", "制剂开发"], ("医疗健康", "生物医药", "制剂研发")),
    (["合成研究", "药化合成", "化学合成"], ("医疗健康", "生物医药", "药物合成")),
    (["分析研究员", "分析方法开发", "质量研究"], ("医疗健康", "生物医药", "药物分析")),
    (["分子生物学", "生物研发", "细胞生物学", "免疫学研究"], ("医疗健康", "生物医药", "生物学研究人员")),
    (["原料生产", "工艺岗", "生产工艺"], ("医疗健康", "生物医药", "药品生产")),
    (["器械注册"], ("医疗健康", "医疗器械", "医疗器械注册")),
    (["注册专员", "注册事务"], ("医疗健康", "生物医药", "药品注册")),
    (["医药项目", "临床项目", "药物研发项目"], ("医疗健康", "生物医药", "医药项目经理")),
    (["临床技术支持", "技术支持", "信息化工程师", "应用工程师"], ("医疗健康", "生物医药", "医疗产品技术支持")),
    (["医学经理"], ("医疗健康", "临床试验", "临床医学经理/专员")),
    (["临床药理"], ("医疗健康", "生物医药", "药理毒理研究员")),
    (["生物信息", "计算生物", "生信"], ("医疗健康", "生物医药", "生物信息工程师")),
    # 通用岗位（2026-10-06 其他专业批次）
    (["市场营销", "市场专员", "营销策划"], ("市场/公关/广告", "市场营销", "市场营销策划")),
    (["人力资源"], ("人力/行政/法务", "人力资源", "人力资源专员/助理")),
    (["行政管理", "综合管理", "综合办", "办公室文员"], ("人力/行政/法务", "行政", "行政专员/助理")),
    (["物流管理", "物流工程"], ("物流/仓储/司机", "物流/运输", "物流专员")),
    (["机械设计", "结构设计"], ("生产制造", "机械设计/制造", "机械工程师")),
    (["通信设计", "通信工程"], ("电子/电气/通信", "通信", "通信技术工程师")),
    (["土建", "结构工程", "土木工程"], ("房地产/建筑", "建筑/规划设计", "土木/土建/结构工程师")),
    (["工程测量", "测量员", "测绘"], ("房地产/建筑", "工程管理", "测绘/测量")),
    (["电商专员", "电商运营"], ("客服/运营", "电商运营", "国内电商运营")),
    (["英语老师"], ("教育培训", "教师", "英语教师")),
    (["体育老师"], ("教育培训", "运动健身", "体育/体能老师")),
    (["讲师"], ("教育培训", "教师", "高校教师/辅导员")),
]


def map_role(role: str, leaves: list) -> tuple[str | None, str]:
    """岗位名 → 树节点。先查补充节点的关键词（更具体），再查 BOSS 末级名称包含关系；都不中返回 None。"""
    r = re.sub(r"\d+$", "", ROLE_NOISE.sub("", role or "").strip()).replace("医师", "医生")  # 招聘写“医师”，BOSS 分类写“医生”
    generic = [x for x in SUPPLEMENT if x[0].startswith("临床医生")]
    for name, parent, keys in [x for x in SUPPLEMENT if x not in generic]:  # 先匹配具体补充节点
        if any(k.lower() in r.lower() for k in keys):
            return SEP.join(parent + (name,)), "关键词"
    if len(re.findall(r"类(?:[|,，、]|$)", role or "")) >= 2:  # “综合管理类|经济金融类”是岗位大类清单，不具体
        return None, "多个岗位大类"
    for keys, path in PRE_ALIASES:
        if any(k in r for k in keys):
            return SEP.join(path), "别名"
    best = None  # (分数, 路径)：完整名称命中 > 科室等简称命中，同级取更长的
    for name, path in leaves:
        for i, x in enumerate(leaf_alts(name)):
            # 两个字的名称（培训、数据、护士）只认出现在岗位名末尾，避免“规范化培训住院医师”挂到“培训”
            hit = (x in r) if len(x) > 2 else r.endswith(x)
            if hit:
                # 只有完整名称（或不含“/”的名称）算完整命中；“分公司/代表处负责人”拆出的“分公司”只算低分
                score = (100 if x == name or ("/" not in name and i == 0) else 0) + len(x)
                if best is None or score > best[0]:
                    best = (score, path)
    if best:
        return best[1], "BOSS末级名称"
    for keys, path in ALIASES:
        if any((k in r) if len(k) > 2 else r.endswith(k) for k in keys):
            return SEP.join(path), "别名"
    for name, parent, keys in generic:  # 最后才用“医生/医师”这类泛称兜底
        if any(k in r for k in keys):
            return SEP.join(parent + (name,)), "关键词"
    return None, "未归类"


NOT_MAJOR = r"(?![一二三四六]?级|考试|水平|能力|证书|成绩)"  # “英语六级”是语言要求，不是英语专业


def has_major(text: str, name: str) -> bool:
    return re.search(re.escape(name) + NOT_MAJOR, text) is not None


def major_classes(rec: dict) -> tuple[list, str]:
    raw = rec.get("majors_raw") or ""
    if re.search(r"不限", raw):
        return ["不限专业"], "需求专业字段"
    if re.search(r"[\u4e00-\u9fff]", raw):
        found = [c for c, names in MAJOR_CLASSES.items() if any(has_major(raw, n) for n in names if not n.isascii())]
        if found:
            return found, "需求专业字段"
    # 字段缺失时，只从职责原文里找完整专业名（≥3 字），避免“临床”“生物”这类短词误配
    desc = rec.get("description") or ""
    found = [c for c, names in MAJOR_CLASSES.items()
             if any(len(n) >= 3 and re.search(re.escape(n) + NOT_MAJOR + r".{0,12}专业", desc) for n in names)]
    if found:
        return found, "职责原文"
    tags = [c for c, names in MAJOR_CLASSES.items() if any(n.isascii() and re.search(rf"\b{n}\b", raw) for n in names)]
    return tags, ("平台专业标签" if tags else "未写")


EDU_RANK = {"大专": 1, "本科": 2, "硕士": 3, "博士": 4}


def edu_from_text(desc: str) -> str | None:
    """正文里写明的学历要求取最低的那个（“博士学历，或取得硕士学历并有3年经验”说明硕士也能报）；没写返回 None。"""
    hits = re.findall(r"(博士|硕士|研究生|本科|大专|专科)(?:研究生)?(?:及以上|以上|学历|学位)", desc or "")
    levels = [{"研究生": "硕士", "专科": "大专"}.get(h, h) for h in hits]
    return min(levels, key=EDU_RANK.get) if levels else None


def edu_level(s: str | None) -> str:
    s = s or ""
    for k, v in (("博士", "博士"), ("硕士", "硕士"), ("研究生", "硕士"), ("本科", "本科"), ("大专", "大专"), ("专科", "大专")):
        if k in s:
            return v
    return "未写"


DUTY_VERB = re.compile(r"负责|协助|参与|完成|开展|进行|撰写|书写|审核|维护|收集|整理|跟进|处理|执行|指导|组织|建立|制定|配合|接待|观察|推广|拜访|诊断|治疗|检查|评估|监测|分析|设计|研发|编辑|校对|筛选|随访|培训|沟通")
NOT_DUTY = re.compile(r"\d+\s*(?:元|万|k|K|年|月|日|人|届)|有限公司|医院$|集团|招聘|学历|专业|岗位名称|发布|地点|来源|薪|校区|公告|职位|优先|具备|具有|熟悉|熟练|能力|精神|介绍链接")


def duty_lines(desc: str) -> list:
    """职责原句：取“职责”段里 8–40 字、含工作动作、不含金额/日期/单位名的句子，逐字来自原文。"""
    part = re.split(r"任职(?:要求|资格|条件)|岗位要求|职位要求|应聘条件|招聘条件", desc)[0]
    out = []
    for line in re.split(r"[\n；;。]", part):
        line = re.sub(r"^\s*[\d一二三四五六七八九十①②③④⑤⑥]+[、.．)）]?\s*", "", line).strip(" ：:\"“”")
        if 8 <= len(line) <= 40 and DUTY_VERB.search(line) and not NOT_DUTY.search(line):
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
    recs = [json.loads(l) for l in POSTINGS.read_text(encoding="utf-8").split("\n") if l.strip()]
    singles, seen_keys = [], set()
    for r in [r for r in recs if r["kind"] == "single"] + load_manual():
        key = (r.get("company"), ROLE_NOISE.sub("", r.get("role") or ""), r.get("majors_raw"))
        if key in seen_keys and not r.get("manual"):  # 同一家公司重复发同一岗位只算一份
            continue
        seen_keys.add(key)
        singles.append(r)
    cards = defaultdict(lambda: {"samples": [], "edu": Counter(), "majors": Counter(), "duties": [], "titles": Counter(), "manual": 0})
    edges = defaultdict(lambda: {"n": 0, "tag_n": 0, "edu": Counter(), "ids": [], "companies": set()})
    unmapped = Counter()
    for r in singles:
        path, how = map_role(r["role"], leaves)
        classes, msrc = major_classes(r)
        edu = edu_level(r.get("education"))
        text_edu = edu_from_text(r.get("description") or "")
        # 结构字段与正文不一致（AIDD 例：字段“硕士”、正文“博士学历”；或一页多岗）：不替招聘方选，标出来让用户去问
        r["edu_conflict"] = bool(text_edu and edu != "未写" and text_edu != edu)
        if r["edu_conflict"]:
            edu = "字段与正文不一致"
        elif text_edu and edu == "未写":
            edu = text_edu
        r.update(node=path, node_match=how, major_classes=classes, major_source=msrc, edu_level=edu)
        if not path:
            unmapped[ROLE_NOISE.sub("", r["role"]).strip()] += 1
            continue
        c = cards[path]
        c["samples"].append(r["url"]); c["manual"] += bool(r.get("manual")); c["edu"][edu] += 1; c["titles"][r["role"]] += 1
        for m in classes:
            c["majors"][m] += 1
            e = edges[(m, path)]
            if msrc == "平台专业标签":
                e["tag_n"] += 1
                continue
            e["n"] += 1; e["edu"][edu] += 1; e["ids"].append(r["url"]); e["companies"].add(r.get("company"))
        for d in duty_lines(r.get("description") or ""):
            if d not in c["duties"] and len(c["duties"]) < 5:
                c["duties"].append(d)
    missing = {r["node"] for r in singles if r.get("node") and r["node"] not in nodes}
    if missing:  # 别名或补充节点写错路径会让样本挂到不存在的节点上：直接失败，不静默
        raise SystemExit(f"路径不在岗位树里：{sorted(missing)}")
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
    edge_out = [{"major_class": m, "node": p, "n": e["n"], "company_n": len(e["companies"]), "platform_tag_only_n": e["tag_n"], "education": dict(e["edu"]),
                 "sample_urls": e["ids"][:5]}
                for (m, p), e in sorted(edges.items(), key=lambda kv: (-len(kv[1]["companies"]), -kv[1]["n"])) if e["n"]]
    (OUT / "edges.json").write_text(json.dumps(edge_out, ensure_ascii=False, indent=1), encoding="utf-8")
    with (OUT / "postings_mapped.jsonl").open("w", encoding="utf-8") as f:
        for r in singles:
            f.write(json.dumps({k: r.get(k) for k in ("id", "url", "company", "role", "node", "node_match", "major_classes",
                                                         "major_source", "edu_level", "edu_conflict", "posted", "archived", "source", "manual")},
                               ensure_ascii=False) + "\n")
    stats = {"postings_total": len(recs), "single": len(singles), "mapped": len(singles) - sum(unmapped.values()),
             "unmapped": sum(unmapped.values()), "nodes_with_samples": len(cards), "edges": len(edge_out),
             "boss_leaves": len(leaves), "supplement_nodes": len(SUPPLEMENT)}
    (OUT / "stats.json").write_text(json.dumps({**stats, "unmapped_top": unmapped.most_common(40)}, ensure_ascii=False, indent=1), encoding="utf-8")
    write_report(card_out, edge_out, stats, unmapped)
    write_all_report(edge_out, stats)
    print(json.dumps(stats, ensure_ascii=False))


def write_report(cards: dict, edges: list, stats: dict, unmapped: Counter) -> None:
    """给人看的医学全景：每个医学专业类 → 大类 → 中类 → 岗位（样本数、学历分布）。"""
    lines = ["# 医学类专业 → 岗位全景（职业库 v2，自动生成）", "",
             "- 生成：scripts/careerdb/build.py；数据：牛企直聘校招单岗页（站内搜索第一页，2026-10-05 抓取）+ BOSS 职位分类树",
             "- 计数是本次抓到的校招样本数，不是全国岗位数；学历是样本页面写的最低要求。",
             "- 专业连线只用招聘原文（需求专业字段或职责原文）；只有平台拼音专业标签的样本不计入。",
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
                items = "；".join(f"{e['node'].split(SEP)[-1]} {e['n']}条/{e['company_n']}家（{'、'.join(f'{k}{v}' for k, v in e['education'].items())}）"
                                 for e in sorted(es2, key=lambda x: (-x["company_n"], -x["n"])))
                lines.append(f"  - {b}：{items}")
        lines.append("")
    lines += ["## 医疗相关全部岗位清单（含暂无样本的）", "",
              "BOSS 医疗健康大类全部末级 + 招聘样本补充节点。“仅分类名称”表示本次没有抓到样本：可以列名字，不能说门槛。", ""]
    groups = defaultdict(list)
    for path, c in cards.items():
        a, b, name = path.split(SEP)
        if c["source"] == "招聘样本补充" and not c["sample_n"]:
            continue
        if a == "医疗健康" or c["source"] == "招聘样本补充":
            groups[f"{a} › {b}"].append(c)
    for g, cs in groups.items():
        items = "；".join(f"{c['name']}（{c['sample_n']} 条样本）" if c["sample_n"] else f"{c['name']}（仅分类名称）"
                         for c in sorted(cs, key=lambda c: -c["sample_n"]))
        lines.append(f"- {g}：{items}")
    lines.append("")
    lines += ["## 未归类岗位名（高频，待补充节点）", "", "、".join(f"{k}×{v}" for k, v in unmapped.most_common(40)), ""]
    (REPORT / "careerdb-medical-v1.md").write_text("\n".join(lines), encoding="utf-8")


def write_all_report(edges: list, stats: dict) -> None:
    """全专业版：每个专业类 → 有样本的岗位（按样本数），一行一类，便于先看广度。"""
    by = defaultdict(list)
    for e in edges:
        by[e["major_class"]].append(e)
    lines = ["# 全专业 → 岗位全景（职业库 v2，自动生成）", "",
             "- 数据与限制同医学版：牛企直聘校招单岗页，每个关键词只取搜索第一页；计数是样本数，不是市场岗位数。",
             f"- 样本 {stats['single']} 条（同公司同岗位重复帖已去重），挂上岗位树 {stats['mapped']} 条；专业连线只用招聘原文。",
             "- 每个岗位后的数字是发布该岗位的不同单位数，只有 1 家的说明证据很薄。", ""]
    for m, es in sorted(by.items(), key=lambda kv: -sum(x["n"] for x in kv[1])):
        es = sorted(es, key=lambda x: (-x["company_n"], -x["n"]))
        lines.append(f"## {m}（{len(es)} 个岗位，{sum(x['n'] for x in es)} 条样本）")
        lines.append("")
        lines.append("；".join(f"{x['node'].split(SEP)[-1]}（{x['node'].split(SEP)[0]}）{x['company_n']}家" for x in es[:30]))
        lines.append("")
    (REPORT / "careerdb-all-v1.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
