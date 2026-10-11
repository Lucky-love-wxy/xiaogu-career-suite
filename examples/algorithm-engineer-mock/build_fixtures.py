#!/usr/bin/env python3
"""用模拟 JD + 真实本地检索结果 + 模拟从业者帖子，生成各实时来源状态下的标准回答。

Usage: python3 build_fixtures.py
Output: responses/<场景>.json（渲染器输入）与 expected/<场景>.md（渲染器逐字输出）。
话术规则见 skills/xiaogu-career-master/references/phrasing.md；本脚本只是把规则落成可回归的样例。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDERER = HERE.parents[1] / "skills" / "xiaogu-career-master" / "scripts" / "render_response.py"

SCOPE_NOTE = {"same_company": "说的就是这家公司", "same_role": "同类岗位，不是这家公司", "different_team": "其他团队，只能间接参考", "unknown": "未说明公司和团队"}


def base(card: dict) -> dict:
    """三层中的前两层：JD 原文与本地数据库。这部分在所有场景里不变。"""
    risk = card["risks"][0]["text"]
    return {
        "fixture": True,
        "status": "complete",
        "answer": (
            "推荐算法工程师主要是用数据和线上实验，让用户更容易刷到可能喜欢的内容。"
            "这份招聘说明写清了要做什么：召回排序模型（决定给用户推什么、按什么顺序推）、特征和线上实验；"
            "但没写团队规模、晋升路径，也没说明“不强制加班”实际怎么执行。"
        ),
        "evidence": [
            {"kind": "jd_fact", "text": "“负责信息流推荐系统的召回、排序模型的设计与优化，提升点击率与用户时长”"},
            {"kind": "jd_fact", "text": "“弹性工作，不强制加班，免费晚餐，年终奖2-4个月”"},
            {"kind": "reference", "text": f"同类岗位一般情况，{risk}。"},
            {"kind": "reference", "text": "“年终奖2-4个月”在招聘话术里通常不是固定发放，要问清按什么算、去年团队实际拿到多少。"},
        ],
        "unknown": ["团队规模和汇报关系（招聘说明没写）", "晋升路径（招聘说明没写）"],
        "next_action": "问招聘方一句：数据、特征、模型和上线工作大概各占多少时间，晚上和周末的消息需要多快回复？",
    }


def post_evidence(post: dict, style: str) -> dict:
    """单条从业者说法。style=scope 时把作者身份和适用范围写在句首，新手不用自己判断能信几分。"""
    claim = post["claims"][0]
    text = claim["paraphrase"]
    if style == "scope":
        scope = SCOPE_NOTE[post["scope"]]
        stale = "，帖子较早，可能已过时" if post["posted_at"] < "2025" else ""
        text = f"（{post['author_label']}；{scope}{stale}）{text}"
    return {"kind": "external_report", "text": text, "url": post["url"], "date": post["posted_at"], "source_name": post["source_name"]}


def build(card: dict, data: dict) -> dict[str, dict]:
    posts = {p["id"]: p for p in data["posts"]}
    pick = lambda scenario: [posts[i] for s in data["scenarios"][scenario]["sources"].values() for i in s["posts"]]
    out: dict[str, dict] = {}

    # 决策点 A：完整命中时，从业者说法怎么呈现（三个变体，等用户选）
    for variant, style, summary in (
        ("full__A1_label", "plain", ""),
        ("full__A2_scope", "scope", ""),
        ("full__A3_summary", "plain", "找到 3 条同类岗位的从业者分享：2 条提到大部分时间在处理数据和实验，1 条说所在组实行大小周。"),
    ):
        r = base(card)
        # 帖子都不是这家公司的：只能说“同类岗位有人反映”，不能说和这份 JD 冲突
        if summary:
            r["answer"] += summary + "这些都不是这家公司的情况，这家是否大小周，招聘说明的“不强制加班”回答不了，需要当面问清。"
        else:
            r["answer"] += "同类岗位有人反映大小周；这家是否如此，招聘说明的“不强制加班”回答不了，需要当面问清。"
        r["evidence"] += [post_evidence(p, style) for p in pick("full")]
        r["unknown"].insert(0, "这家公司推荐组实际是否大小周（同类岗位有人反映，这家未知）")
        out[variant] = r

    # 只有明确指向这家公司的帖子，才用“对不上”的冲突措辞
    r = base(card)
    r["answer"] += "有自称这家公司推荐组在职的人说组里实行大小周，和招聘说明的“不强制加班”对不上，需要当面问清。"
    r["evidence"] += [post_evidence(p, "scope") for p in pick("same_company_conflict")]
    r["unknown"].insert(0, "这个团队是否大小周（这家公司从业者的说法与招聘说明冲突）")
    out["same_company_conflict"] = r

    r = base(card)
    r["answer"] += "唯一找到的从业者分享是 2022 年的，只能当作当时的情况参考。"
    r["evidence"] += [post_evidence(p, "scope") for p in pick("stale_only")]
    r["unknown"].append("近一年从业者的实际说法（只找到较早的分享）")
    out["stale_only"] = r

    r = base(card)
    r["answer"] += "只找到一条匿名说法，信息太少，不能当成这个岗位的实际情况。"
    r["evidence"] += [post_evidence(p, "scope") for p in pick("single_anonymous")]
    r["unknown"].append("加班情况（只有一条无法核实的匿名说法）")
    out["single_anonymous"] = r

    r = base(card)
    r["answer"] += "找到的分享来自搜索算法团队，不是推荐团队，只能间接参考。"
    r["evidence"] += [post_evidence(p, "scope") for p in pick("different_team")]
    r["unknown"].append("推荐团队从业者的实际说法（目前只有相邻团队的分享）")
    out["different_team"] = r

    # 决策点 B：完全没有从业者分享时怎么说（两个变体，等用户选）
    r = base(card)
    r["unknown"].append("从业者的实际说法：这次没找到相关分享，以上判断只基于招聘说明和资料库")
    out["no_results__B1_unknown"] = r
    r = base(card)
    r["unknown"].append("从业者的实际说法：这次没找到相关分享，以上判断只基于招聘说明和资料库")
    r["next_action"] = "请招聘方安排你和团队里的工程师聊 10 分钟，直接问他上周具体做了哪些事。"
    out["no_results__B2_action"] = r

    r = base(card)
    r["evidence"] += [post_evidence(p, "scope") for p in pick("robots_blocked")]
    r["unknown"].append("脉脉上的说法：这个网站不允许当前工具读取，这次只参考了牛客的一条分享")
    out["robots_blocked"] = r
    return out


def main() -> int:
    card = json.loads((HERE / "job_card.json").read_text(encoding="utf-8"))["card"]
    data = json.loads((HERE / "live_sources.json").read_text(encoding="utf-8"))
    (HERE / "responses").mkdir(exist_ok=True)
    (HERE / "expected").mkdir(exist_ok=True)
    for name, payload in build(card, data).items():
        source = HERE / "responses" / f"{name}.json"
        source.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(RENDERER), str(source)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{name}: {result.stderr.strip()}", file=sys.stderr)
            return 1
        (HERE / "expected" / f"{name}.md").write_text(result.stdout, encoding="utf-8")
        print(name, len(payload["answer"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
