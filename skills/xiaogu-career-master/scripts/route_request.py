#!/usr/bin/env python3
"""Route one natural-language request to the Xiaogu skill pipeline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PATTERNS = {
    "external_research": r"脉脉|职场社区|从业者.{0,6}(评价|分享|怎么说)|公司口碑|真实员工|真实体验",
    "interview": r"面试.{0,20}(复盘|答|回忆|记录|刚|完|录音)|复盘.{0,12}面试|逐字稿|面试录音|面试记录|回答得怎么样|模拟面试",
    "resume": r"简历|项目经历|自我介绍|经历.{0,6}(改写|润色)|匹配.{0,6}经历",
    # 只认“替我去搜/找具体岗位列表”；“现在找工作来得及吗”这类泛问不算
    "jobs": r"(?:找|搜|搜索|推荐).{0,8}(?:岗位|职位|工作机会)|岗位推荐|职位推荐|BOSS|Boss直聘|招聘机会",
    "job_understanding": r"JD|招聘说明|招聘信息|招聘广告|招聘要求|任职要求|(?:岗位|职位|这份工作|这工作|工程师|产品经理|运营|设计师).{0,12}(做什么|干什么|怎么样|值不值得|靠谱吗|适合|能做)|行业黑话|招聘话术|结果导向|快速迭代|主人翁|薪资面议|核实问题",
    "jargon": r"扁平化管理|弹性工作|14薪|13薪|年薪范围|带薪年假|调休|团建|公司旅游|全额五险一金|有竞争力的薪酬|绩效奖金|房补|餐补|黑话.{0,8}(什么意思|翻译)|(?:招聘话术|福利).{0,8}(什么意思|怎么算)",
    "next_step": r"下一步|怎么开始|带我求职|帮我求职|继续上次|现在该做什么|从头开始",
    "onboarding": r"(?:没|没有|不)(?:用过|懂|会).{0,5}AI|第一次.{0,8}(AI|用|求职)|从哪开始|不知道.{0,6}(开始|怎么找工作)",
    "application_feedback": r"(?:投|投递).{0,20}(没回|没有回|拒|失败|没消息|没动静)|面试通过.{0,8}(offer|录用)|审批中|口头offer|求职复盘",
}


def matches(name: str, query: str) -> bool:
    if name == "jargon":
        path = Path(__file__).resolve().parents[1] / "references" / "routing-jargon.json"
        if path.exists():
            compact = re.sub(r"\s+", "", query).lower()
            if any(re.sub(r"\s+", "", term).lower() in compact for term in json.loads(path.read_text(encoding="utf-8"))):
                return True
    return re.search(PATTERNS[name], query, re.IGNORECASE) is not None


def has_material(query: str, kind: str, context: dict[str, Any]) -> bool:
    """Distinguish supplied content from phrases such as “这份 JD”."""
    context_keys = {
        "job": "has_job_description",
        "experience": "has_candidate_experience",
        "transcript": "has_interview_transcript",
    }
    if context.get(context_keys[kind]) is True:
        return True
    if kind == "job":
        return bool(re.search(r"(?:招聘说明|招聘信息|JD|岗位描述)[：:].*(?:负责|要求|职责)", query, re.I | re.S)) or len(query) >= 70 and bool(re.search(r"职责|要求|薪资|任职|工作内容|职位描述|岗位描述|职位详情|加班|双休|经验", query, re.I))
    if kind == "experience":
        return len(query) >= 60 and bool(re.search(r"我(?:负责|做过|主导|参与)|提升|降低|完成|结果", query, re.I))
    return bool(re.search(r"面试官(?:问|[：:]).+?我回答[：:]?.+", query, re.S)) or len(query) >= 100 and bool(re.search(r"面试官|(?:^|\n)\s*[Q问答A][：:]|我回答", query, re.I))


# 岗位理解默认附带的实时来源，按优先级排列。牛客在前：robots 对所有代理只禁 /search，
# 校招面经贴合新手；脉脉只读 robots 放行的公开详情页。顺序待 Codex 调研（notes/2026-10-03）后校正。
LIVE_SOURCES = ["nowcoder", "maimai"]


def live_sources_for(query: str, pipeline: list[str]) -> list[str]:
    """只给“理解岗位”配实时来源；单问黑话、改简历、面试复盘不默认联网。"""
    if "xiaogu-resume" in pipeline or "xiaogu-interview-review" in pipeline:
        return []
    if matches("external_research", query):
        return list(LIVE_SOURCES)
    # “结果导向是什么意思”这类单问黑话也会命中岗位理解正则；没有岗位名词或 JD 时不联网
    if matches("job_understanding", query) and (
        re.search(r"工程师|经理|专员|顾问|设计师|分析师|运营|岗位|职位|这份工作|这工作|JD|招聘说明|招聘信息", query, re.I)
    ):
        return list(LIVE_SOURCES)
    return []


def route(query: str, context: dict[str, Any] | None = None) -> dict:
    context = context or {}
    pipeline: list[str] = []
    reasons: list[str] = []

    concrete = any(matches(kind, query) for kind in ("job_understanding", "jargon", "resume", "interview"))
    feedback_only = matches("application_feedback", query) and not any(matches(kind, query) for kind in ("job_understanding", "jargon", "interview", "external_research")) and not re.search(r"改|润色|优化|复盘面试", query)
    if (matches("onboarding", query) and not concrete) or feedback_only:
        return {
            "status": "routed", "primary_skill": "xiaogu-career-master",
            "pipeline": ["xiaogu-career-master"],
            "reason": ["先引导首次使用或整理求职进度，再决定具体功能"],
            "missing_inputs": [],
            "live_sources": [],
            "next_action": "读取已提供的目标或进度；没有时只询问目前想解决的一个问题",
        }

    if matches("external_research", query):
        pipeline.extend(["web-access", "xiaogu-career-suite"])
        reasons.append("用户明确要求使用外部职场社区或从业者资料")
    if matches("jobs", query):
        pipeline.append("xiaogu-boss-jobs")
        reasons.append("用户想发现或读取岗位")
    if matches("job_understanding", query) or matches("jargon", query):
        if "xiaogu-career-suite" not in pipeline:
            pipeline.append("xiaogu-career-suite")
        reasons.append("用户想理解岗位、JD、招聘话术或核实问题")
    if matches("resume", query):
        if "xiaogu-career-suite" not in pipeline:
            pipeline.append("xiaogu-career-suite")
        pipeline.append("xiaogu-resume")
        reasons.append("定制简历前需要先理解目标岗位")
    if matches("interview", query):
        if "xiaogu-career-suite" not in pipeline:
            pipeline.append("xiaogu-career-suite")
        pipeline.append("xiaogu-interview-review")
        reasons.append("面试复盘需要岗位背景和面试原始记录")
    if matches("next_step", query) and not pipeline:
        pipeline.append("xiaogu-career-master")
        reasons.append("用户希望读取进度或由总控决定下一步")

    if not pipeline:
        return {
            "status": "needs_clarification",
            "primary_skill": "xiaogu-career-master",
            "pipeline": [],
            "live_sources": [],
            "question": "你现在最想解决哪件事：找岗位、看懂 JD、改简历，还是复盘面试？",
        }

    missing = []
    has_job = has_material(query, "job", context)
    if "xiaogu-resume" in pipeline:
        # 岗位版简历必须有招聘说明正文；岗位名称或“这份 JD”这类指代都不够
        if not has_job:
            missing.append("目标岗位的招聘说明")
    elif "xiaogu-career-suite" in pipeline and "xiaogu-interview-review" not in pipeline and not matches("jargon", query) and not has_job and not re.search(
        # 后缀必须出现：单独的“数据”“产品”“测试”不算岗位名称
        r"(?:工程师|经理|专员|顾问|设计师|分析师|架构师|程序员|运营|审核员|产品经理)",
        query,
        re.IGNORECASE,
    ):
        missing.append("岗位名称或 JD")
    if "xiaogu-resume" in pipeline and not has_material(query, "experience", context):
        missing.append("经过本人确认的经历或现有简历")
    if "xiaogu-interview-review" in pipeline and not has_material(query, "transcript", context):
        missing.append("逐字稿或完整面试问答")

    return {
        "status": "routed",
        "primary_skill": pipeline[-1],
        "pipeline": pipeline,
        "reason": reasons,
        "missing_inputs": missing,
        "live_sources": live_sources_for(query, pipeline),
        "next_action": "先索取最前面的缺失材料" if missing else "直接执行整条 pipeline",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--context-json", default="{}", help="JSON flags for materials already attached or saved")
    args = parser.parse_args()
    context = json.loads(args.context_json)
    print(json.dumps(route(args.query, context), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
