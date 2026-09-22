#!/usr/bin/env python3
"""Create a provenance-labelled occupation reality card from a title or JD."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from search_occupations import search


ROOT = Path(__file__).resolve().parents[1]
PROJECT_TAXONOMY = ROOT.parents[1] / "database" / "taxonomy.json"
BUNDLED_TAXONOMY = ROOT / "references" / "taxonomy.json"
TAXONOMY_PATH = BUNDLED_TAXONOMY if BUNDLED_TAXONOMY.exists() else PROJECT_TAXONOMY
TAXONOMY = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


FIELD_PATTERNS = {
    "compensation": r"薪资|工资|月薪|年薪|薪酬|\b\d+[kK]\b",
    "working_hours": r"工作时间|工时|双休|大小周|排班|值班|加班",
    "metrics": r"KPI|指标|转化率|准确率|点击率|销售额|利润|ROI|留存|可用性",
    "team": r"团队|汇报|下属|跨部门|协作|对接",
    "decision_rights": r"独立负责|决策权|审批|预算|制定.*策略|主导",
    "promotion": r"晋升|发展路径|培养|轮岗|转岗",
}

CONFLICT_PATTERNS = [
    ("双休", r"单休|大小周", "休息制度同时出现双休与单休/大小周"),
    ("不加班", r"经常加班|接受加班|加班是常态", "工时描述同时出现不加班与常态加班"),
    ("无需出差", r"经常出差|长期出差|驻场", "出差描述同时出现无需出差与经常出差/驻场"),
]


def compact_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)、])\s*", "", raw).strip()
        if line and line not in lines:
            lines.append(line)
    if len(lines) == 1 and len(lines[0]) > 160:
        lines = [part.strip() for part in re.split(r"[。；;]", lines[0]) if part.strip()]
    return lines[:40]


def declarative_lines(text: str) -> list[str]:
    request_prefix = re.compile(
        r"^(?:请帮我|帮我|请)(?:分析|解读|看看|看一下)(?:这个岗位|这份JD|这个JD|以下内容)?[：:，,\s]*"
    )
    interrogative = re.compile(r"[?？]$|^(?:什么是|请问|能否|可以吗)")
    lines = []
    for raw in compact_lines(text):
        line = request_prefix.sub("", raw).strip()
        if line and not interrogative.search(line):
            lines.append(line)
    return lines


def disclosed_fields(text: str) -> dict[str, list[str]]:
    lines = compact_lines(text)
    return {
        field: [line for line in lines if re.search(pattern, line, re.I)][:5]
        for field, pattern in FIELD_PATTERNS.items()
    }


def statement(text: str, status: str, source: str, confidence: str) -> dict:
    return {"text": text, "status": status, "source": source, "confidence": confidence}


def detect_conflicts(text: str) -> list[dict]:
    conflicts = []
    for literal, pattern, description in CONFLICT_PATTERNS:
        if literal in text and re.search(pattern, text):
            conflicts.append(statement(description, "conflict", "input", "high"))
    return conflicts


def hierarchy_for(occupation: dict) -> list[dict]:
    chain = [{"id": occupation["id"], "name": occupation["name"]}]
    parent_id = occupation.get("parent_id")
    seen = {occupation["id"]}
    while parent_id:
        if parent_id in seen:
            break
        seen.add(parent_id)
        node = TAXONOMY.get(parent_id)
        if not node:
            chain.insert(0, {"id": parent_id, "name": parent_id, "unresolved": True})
            break
        chain.insert(0, {"id": parent_id, "name": node["name"]})
        parent_id = node.get("parent_id")
    return chain


def occupation_conflicts(text: str, occupation: dict) -> list[dict]:
    conflicts = []
    reference_texts = occupation.get("keywords", []) + occupation.get("daily_work", []) + occupation.get("deliverables", [])
    for match in re.finditer(r"(?:明确不参与|不参与|无需|不涉及|不负责|不用)([^，。；;\n]{1,20})", text):
        excluded = match.group(1).strip()
        if any(excluded in value or value in excluded for value in reference_texts if len(value) >= 2):
            conflicts.append(statement(
                f"JD明确排除“{excluded}”，但职业索引将其列为常见工作，需要确认岗位边界。",
                "conflict",
                "input+occupation_index",
                "high",
            ))
    return conflicts


def analyze(text: str) -> dict:
    search_result = search(text, limit=3)
    fields = disclosed_fields(text)
    lines = compact_lines(text)
    result = {
        "schema_version": "1.0",
        "input": {"text": text, "extracted_lines": lines},
        "match": {
            "status": search_result["status"],
            "selected": None,
            "alternatives": [],
        },
        "card": {
            "plain_language": None,
            "occupation_inference": None,
            "jd_facts": [],
            "conflicts": detect_conflicts(text),
            "keywords": [],
            "daily_work": [],
            "deliverables": [],
            "metrics": [],
            "growth": [],
            "risks": [],
            "questions": [],
            "unknowns": [],
            "unknown_fields": [],
            "evidence": [],
        },
        "validation_hints": [],
    }
    if search_result["status"] == "index_miss":
        result["card"]["unknown_fields"] = ["occupation_baseline"] + [
            field for field, matched_lines in fields.items() if not matched_lines
        ]
        for line in declarative_lines(text):
            fact = statement(line, "jd_fact", "input", "high")
            fact["fields"] = ["input_statement"]
            result["card"]["jd_facts"].append(fact)
        result["card"]["unknowns"] = [
            statement(f"JD未披露：{field}", "unknown", "analyzer", "high")
            for field in result["card"]["unknown_fields"]
        ]
        result["validation_hints"].append("职业索引未命中：只能复述输入事实，不得补充行业惯例。")
        return result

    selected = search_result["matches"][0]
    occupation = selected["occupation"]
    result["match"]["selected"] = {
        "id": occupation["id"],
        "name": occupation["name"],
        "confidence": selected["confidence"],
        "matched_terms": selected["matched_terms"],
        "parent_id": occupation.get("parent_id"),
        "hierarchy": hierarchy_for(occupation),
    }
    result["match"]["alternatives"] = [
        {"id": row["occupation"]["id"], "name": row["occupation"]["name"], "confidence": row["confidence"]}
        for row in search_result["matches"][1:]
    ]
    base_confidence = "medium" if selected["confidence"] == "high" else "low"
    result["card"]["occupation_inference"] = statement(
        f"输入最可能对应“{occupation['name']}”。",
        "inference",
        "matcher",
        selected["confidence"],
    )
    result["card"]["plain_language"] = statement(
        occupation["plain_language"], "reference", f"occupation:{occupation['id']}", base_confidence
    )
    for key in ("keywords", "daily_work", "deliverables", "metrics", "growth", "risks"):
        result["card"][key] = [
            statement(value, "reference", f"occupation:{occupation['id']}", base_confidence)
            for value in occupation.get(key, [])
        ]
    result["card"]["questions"] = occupation.get("questions", [])[:3]
    result["card"]["evidence"] = occupation.get("evidence", [])

    fact_map: dict[str, list[str]] = {line: ["input_statement"] for line in declarative_lines(text)}
    for field, matched_lines in fields.items():
        if matched_lines:
            for line in matched_lines:
                fact_map.setdefault(line, []).append(field)
        else:
            result["card"]["unknown_fields"].append(field)
    for line, fact_fields in fact_map.items():
        fact = statement(line, "jd_fact", "input", "high")
        fact["fields"] = fact_fields
        result["card"]["jd_facts"].append(fact)
    result["card"]["conflicts"].extend(occupation_conflicts(text, occupation))
    result["card"]["unknowns"] = [
        statement(f"JD未披露：{field}", "unknown", "analyzer", "high")
        for field in result["card"]["unknown_fields"]
    ]
    if selected["confidence"] == "medium":
        result["validation_hints"].append("只命中多个专业关键词，职业身份仍需用户确认。")
    if result["match"]["alternatives"]:
        result["validation_hints"].append("存在相邻职业候选，输出时应说明可能的岗位混合。")
    return result


def render_markdown(result: dict) -> str:
    selected = result["match"]["selected"]
    if not selected:
        card = result["card"]
        lines = ["# 岗位现实卡", "", "职业索引未命中。当前只能复述输入信息，需要新增或确认职业条目。"]
        if card["jd_facts"]:
            lines += ["", "## 输入明确写了什么", ""] + [f"- {item['text']}" for item in card["jd_facts"]]
        lines += ["", "## 当前未知", "", "、".join(card["unknown_fields"])]
        return "\n".join(lines)
    card = result["card"]
    lines = [
        f"# {selected['name']}｜岗位现实卡",
        "",
        f"**召回置信度：** {selected['confidence']}",
        f"**职业层级：** {' > '.join(node['name'] for node in selected['hierarchy'])}",
        "",
        f"**一句话：** {card['plain_language']['text']}",
        "",
        "**关键词：** " + "、".join(item["text"] for item in card["keywords"][:6]),
        "",
    ]
    if card["jd_facts"]:
        lines += ["## JD明确写了什么", ""]
        lines += [f"- [{'/'.join(item['fields'])}] {item['text']}" for item in card["jd_facts"]]
        lines.append("")
    if card["conflicts"]:
        lines += ["## JD内部冲突", ""]
        lines += [f"- {item['text']}" for item in card["conflicts"]]
        lines.append("")
    sections = [
        ("每天主要做什么", "daily_work"),
        ("交付什么", "deliverables"),
        ("通常看什么指标", "metrics"),
        ("可能积累什么", "growth"),
        ("主要风险", "risks"),
    ]
    for title, key in sections:
        lines += [f"## {title}", ""]
        for item in card[key]:
            label = "JD明确" if item["status"] == "jd_fact" else "职业参考"
            lines.append(f"- [{label}] {item['text']}")
        lines.append("")
    lines += ["## 面试核实问题", ""] + [f"- {q}" for q in card["questions"]]
    lines += ["", "## 当前未知", "", "、".join(card["unknown_fields"]) or "无"]
    if card["evidence"]:
        lines += ["", "## 证据边界", ""]
        for evidence in card["evidence"]:
            lines.append(f"- [{evidence['type']}] {evidence['title']}：{evidence['scope']}（{evidence['url']}）")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an occupation reality card")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query")
    source.add_argument("--file", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = args.query if args.query is not None else args.file.read_text(encoding="utf-8")
    result = analyze(text)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(result)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
