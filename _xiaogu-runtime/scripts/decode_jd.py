#!/usr/bin/env python3
"""Create an evidence-bound JD check sheet from text or a JobDocument."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOSSARY = ROOT.parents[1] / "database" / "jargon.json"


def load_input(path: Path) -> tuple[str, dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".json":
        return raw, {"source": "user_text", "path": str(path)}
    payload = json.loads(raw)
    if isinstance(payload, dict) and isinstance(payload.get("jobs"), list):
        payload = payload["jobs"][0]
    if not isinstance(payload, dict):
        raise ValueError("JSON input must contain a JobDocument object")
    text = str(payload.get("full_text") or payload.get("description") or "")
    position = payload.get("position") if isinstance(payload.get("position"), dict) else {}
    prefix = "\n".join(
        f"{label}：{position.get(key)}"
        for label, key in (("职位", "title"), ("公司", "company"), ("薪资", "salary"), ("地点", "city"))
        if position.get(key)
    )
    return (prefix + "\n" + text).strip(), {"source": payload.get("source", "job_document"), "job_id": payload.get("id")}


def sentence_for(text: str, start: int, end: int) -> str:
    left = max(text.rfind(mark, 0, start) for mark in ("\n", "。", "；", ";")) + 1
    boundaries = [text.find(mark, end) for mark in ("\n", "。", "；", ";")]
    boundaries = [value for value in boundaries if value >= 0]
    right = min(boundaries) + 1 if boundaries else len(text)
    return text[left:right].strip()


def explicit_claims(text: str) -> list[dict[str, Any]]:
    patterns = {
        "salary": r"(?:薪资|工资|月薪|年薪)[：:\s]*([^\n。；]{2,40})",
        "location": r"(?:地点|工作地址|工作地点)[：:\s]*([^\n。；]{2,50})",
        "experience": r"(?:经验|工作经验)[：:\s]*([^\n。；]{1,30})",
        "education": r"(?:学历|教育背景)[：:\s]*([^\n。；]{1,30})",
    }
    claims = []
    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if match:
            claims.append({
                "field": field,
                "value": match.group(1).strip(),
                "source_quote": sentence_for(text, match.start(), match.end()),
                "source_type": "jd_disclosed",
            })
    return claims


def jargon_matches(text: str, glossary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    occupied: list[tuple[int, int]] = []
    for entry in sorted(glossary, key=lambda item: max([len(item.get("term", ""))] + [len(str(a)) for a in item.get("aliases", [])]), reverse=True):
        terms = [entry.get("term", "")] + [str(alias) for alias in entry.get("aliases", [])]
        for matched_term in filter(None, terms):
          for match in re.finditer(re.escape(matched_term), text, flags=re.I):
            span = match.span()
            if any(not (span[1] <= start or span[0] >= end) for start, end in occupied):
                continue
            occupied.append(span)
            matches.append({
                "term": entry["term"],
                "matched_text": matched_term,
                "source_quote": sentence_for(text, *span),
                "levels": {
                    "literal": entry["literal"],
                    "risk_hypothesis": entry["hypothesis"],
                    "verification": entry["verify"],
                },
                "fields": entry.get("fields", []),
                "confidence": "dictionary_match",
            })
    return sorted(matches, key=lambda item: text.find(item["term"]))


def missing_fields(text: str, claims: list[dict[str, Any]]) -> list[str]:
    present = {claim["field"] for claim in claims}
    keyword_rules = {
        "working_hours": ("工作时间", "工时", "双休", "单休", "排班", "值班"),
        "fixed_pay": ("底薪", "固定工资", "固定月薪"),
        "variable_pay": ("绩效", "提成", "奖金"),
        "team_structure": ("团队", "汇报", "直属"),
        "success_metrics": ("KPI", "指标", "考核", "目标"),
        "resources": ("预算", "资源", "编制", "设计支持", "投放支持"),
    }
    missing = []
    for field, keywords in keyword_rules.items():
        if field in present or any(keyword.lower() in text.lower() for keyword in keywords):
            continue
        missing.append(field)
    return missing


def conflicts(text: str) -> list[dict[str, str]]:
    pairs = [
        (("不强制加班", "拒绝加班"), ("能接受加班", "长期加班", "高强度加班"), "加班表述存在冲突"),
        (("职责明确",), ("完成领导交办的其他任务",), "职责边界表述存在张力"),
    ]
    found = []
    for left, right, label in pairs:
        a = next((term for term in left if term in text), None)
        b = next((term for term in right if term in text), None)
        if a and b:
            found.append({"label": label, "left": a, "right": b, "status": "needs_confirmation"})
    return found


def select_questions(matches: list[dict[str, Any]], missing: list[str], conflicts_found: list[dict[str, str]]) -> list[dict[str, Any]]:
    questions = []
    seen = set()
    for item in matches:
        question = item["levels"]["verification"]
        if question not in seen:
            questions.append({"question": question, "reason": f"JD 使用了“{item['term']}”，具体条件未完全披露。", "source_quote": item["source_quote"]})
            seen.add(question)
        if len(questions) == 3:
            return questions
    generic = {
        "working_hours": "日常、业务高峰和周末分别怎样安排工时？",
        "fixed_pay": "固定月薪、浮动部分和发薪月数分别是多少？",
        "team_structure": "这个岗位向谁汇报，团队如何分工？",
        "success_metrics": "入职前三个月的核心目标和验收指标是什么？",
        "resources": "为了完成目标，岗位可以使用哪些人员、预算和数据资源？",
    }
    for field in missing:
        if field in generic and generic[field] not in seen:
            questions.append({"question": generic[field], "reason": f"JD 未披露 {field}。", "source_quote": None})
            seen.add(generic[field])
        if len(questions) == 3:
            break
    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    args = parser.parse_args()
    text, source = load_input(args.input)
    glossary = json.loads(args.glossary.read_text(encoding="utf-8"))
    claims = explicit_claims(text)
    matches = jargon_matches(text, glossary)
    missing = missing_fields(text, claims)
    conflicts_found = conflicts(text)
    result = {
        "schema_version": "1.0",
        "id": "jd_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": source,
        "source_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "claims": claims,
        "jargon": matches,
        "missing_fields": missing,
        "conflicts": conflicts_found,
        "priority_questions": select_questions(matches, missing, conflicts_found),
        "interpretation_boundary": "literal 为术语释义；risk_hypothesis 是待核实假设；verification 是建议问题。未披露不等于条件不存在。",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(args.output), "jargon_count": len(matches), "question_count": len(result["priority_questions"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
