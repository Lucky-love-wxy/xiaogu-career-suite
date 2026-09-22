#!/usr/bin/env python3
"""Route one natural-language request to the Xiaogu skill pipeline."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any


PATTERNS = {
    "external_research": r"脉脉|职场社区|从业者.{0,6}(评价|分享|怎么说)|公司口碑|真实员工|真实体验",
    "interview": r"面试.{0,12}复盘|复盘.{0,12}面试|逐字稿|面试录音|面试记录|回答得怎么样|模拟面试",
    "resume": r"简历|项目经历|自我介绍|经历.{0,6}(改写|润色)|匹配.{0,6}经历",
    "jobs": r"找岗位|找工作|搜岗位|搜索岗位|职位推荐|岗位推荐|BOSS|Boss直聘|招聘机会",
    "job_understanding": r"JD|(?:岗位|职位|工程师|产品经理|运营|设计师).{0,12}(做什么|干什么|怎么样|值不值得)|行业黑话|招聘话术|结果导向|快速迭代|主人翁|薪资面议|核实问题",
    "next_step": r"下一步|怎么开始|带我求职|帮我求职|继续上次|现在该做什么|从头开始",
}


def matches(name: str, query: str) -> bool:
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
        return len(query) >= 70 and bool(re.search(r"职责|要求|薪资|任职|工作内容|加班|双休|经验", query, re.I))
    if kind == "experience":
        return len(query) >= 60 and bool(re.search(r"我(?:负责|做过|主导|参与)|提升|降低|完成|结果", query, re.I))
    return len(query) >= 100 and bool(re.search(r"面试官|(?:^|\n)\s*[Q问答A][：:]|我回答", query, re.I))


def route(query: str, context: dict[str, Any] | None = None) -> dict:
    context = context or {}
    pipeline: list[str] = []
    reasons: list[str] = []

    if matches("external_research", query):
        pipeline.extend(["web-access", "xiaogu-career-suite"])
        reasons.append("用户明确要求使用外部职场社区或从业者资料")
    if matches("jobs", query):
        pipeline.append("xiaogu-boss-jobs")
        reasons.append("用户想发现或读取岗位")
    if matches("job_understanding", query):
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
            "question": "你现在最想解决哪件事：找岗位、看懂 JD、改简历，还是复盘面试？",
        }

    missing = []
    if "xiaogu-career-suite" in pipeline and not has_material(query, "job", context) and not re.search(
        r"(?:算法|数据|前端|后端|测试|运维|产品|运营|设计|销售|招聘).{0,8}(?:工程师|经理|专员|顾问|设计师)?",
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
