#!/usr/bin/env python3
"""Validate a JSON occupation reality card before model rewriting."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from analyze_job import analyze


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "references" / "output-schema.json").read_text(encoding="utf-8"))
PROJECT_OCCUPATIONS = ROOT.parents[1] / "database" / "occupations.json"
BUNDLED_OCCUPATIONS = ROOT / "references" / "occupations.json"
OCCUPATIONS_PATH = BUNDLED_OCCUPATIONS if BUNDLED_OCCUPATIONS.exists() else PROJECT_OCCUPATIONS
OCCUPATIONS = json.loads(OCCUPATIONS_PATH.read_text(encoding="utf-8"))
OCCUPATION_BY_ID = {item["id"]: item for item in OCCUPATIONS}
STATEMENT_LISTS = ("jd_facts", "conflicts", "keywords", "daily_work", "deliverables", "metrics", "growth", "risks", "unknowns")


def numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?(?:[kKwW]|%|人|年|月|天|小时|条|次)?", text))


def allowed_reference_texts(occupation: dict) -> set[str]:
    texts = {occupation.get("plain_language", "")}
    for field in ("keywords", "daily_work", "deliverables", "metrics", "growth", "risks"):
        texts.update(occupation.get(field, []))
    return texts - {""}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be an object"]
    if data.get("schema_version") != CONTRACT["schema_version"]:
        errors.append("schema_version mismatch")
    card = data.get("card")
    if not isinstance(card, dict):
        return errors + ["card must be an object"]
    for field in CONTRACT["required_card_fields"]:
        if field not in card:
            errors.append(f"missing card field: {field}")
    questions = card.get("questions", [])
    if not isinstance(questions, list):
        errors.append("questions must be a list")
        questions = []
    if len(questions) > CONTRACT["max_questions"]:
        errors.append("more than three questions")
    allowed_statuses = set(CONTRACT["allowed_statement_statuses"])
    allowed_confidences = set(CONTRACT["allowed_confidences"])
    input_block = data.get("input", {})
    if not isinstance(input_block, dict):
        errors.append("input must be an object")
        input_block = {}
    input_text = input_block.get("text", "")
    if not isinstance(input_text, str):
        errors.append("input.text must be a string")
        input_text = ""
    if isinstance(input_text, str) and data != analyze(input_text):
        errors.append("card does not match deterministic analyzer output")
    match_block = data.get("match", {})
    if not isinstance(match_block, dict):
        errors.append("match must be an object")
        match_block = {}
    selected = match_block.get("selected")
    if selected is not None and not isinstance(selected, dict):
        errors.append("match.selected must be an object or null")
        selected = None
    selected_id = selected.get("id") if selected else None
    selected_occupation = OCCUPATION_BY_ID.get(selected_id)
    allowed_references = allowed_reference_texts(selected_occupation) if selected_occupation else set()
    for field in STATEMENT_LISTS:
        items = card.get(field, [])
        if not isinstance(items, list):
            errors.append(f"{field} must be a list")
            continue
        for item in items:
            if not isinstance(item, dict):
                errors.append(f"{field} contains a non-statement")
                continue
            if item.get("status") not in allowed_statuses:
                errors.append(f"{field} has invalid status")
            if item.get("confidence") not in allowed_confidences:
                errors.append(f"{field} has invalid confidence")
            item_text = item.get("text")
            if not isinstance(item_text, str):
                errors.append(f"{field} statement text must be a string")
                item_text = ""
            if item.get("status") == "jd_fact":
                if item.get("source") != "input":
                    errors.append(f"{field} jd_fact source must be input")
                if not item_text.strip():
                    errors.append(f"{field} jd_fact is empty")
                elif item_text not in input_text:
                    errors.append(f"{field} jd_fact is not a verbatim input fragment")
            if item.get("status") == "reference":
                expected_source = f"occupation:{selected_id}"
                if item.get("source") != expected_source:
                    errors.append(f"{field} reference source does not match selected occupation")
                if item_text not in allowed_references:
                    errors.append(f"{field} reference text is absent from selected occupation")
            if item.get("status") == "unknown" and item.get("source") != "analyzer":
                errors.append(f"{field} unknown source must be analyzer")
            if item.get("status") == "conflict":
                source = item.get("source")
                text = item_text
                fixed_conflicts = {
                    "休息制度同时出现双休与单休/大小周",
                    "工时描述同时出现不加班与常态加班",
                    "出差描述同时出现无需出差与经常出差/驻场",
                }
                if source == "input":
                    if text not in fixed_conflicts:
                        errors.append(f"{field} contains an unrecognized input conflict")
                elif source == "input+occupation_index":
                    match = re.fullmatch(r"JD明确排除“(.+)”，但职业索引将其列为常见工作，需要确认岗位边界。", text)
                    excluded = match.group(1) if match else ""
                    if not match or excluded not in input_text or not any(
                        excluded in value or value in excluded for value in allowed_references
                    ):
                        errors.append(f"{field} contains an unverified index conflict")
                else:
                    errors.append(f"{field} conflict source is invalid")
    plain = card.get("plain_language")
    if plain is not None:
        if not isinstance(plain, dict):
            errors.append("plain_language must be a statement or null")
        elif plain.get("status") != "reference":
            errors.append("plain_language must remain a reference")
        else:
            if plain.get("source") != f"occupation:{selected_id}":
                errors.append("plain_language reference source does not match selected occupation")
            if plain.get("text") not in allowed_references:
                errors.append("plain_language reference text is absent from selected occupation")
    inference = card.get("occupation_inference")
    if inference is not None:
        if not isinstance(inference, dict):
            errors.append("occupation_inference must be a statement or null")
        elif inference.get("status") != "inference" or inference.get("source") != "matcher":
            errors.append("occupation_inference must be a matcher inference")
        elif not isinstance(inference.get("text"), str):
            errors.append("occupation_inference text must be a string")
    generated_numbers = set()
    for field in STATEMENT_LISTS:
        items = card.get(field, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and item.get("status") in {"jd_fact", "inference", "conflict"}:
                item_text = item.get("text")
                if isinstance(item_text, str):
                    generated_numbers |= numbers(item_text)
    if isinstance(inference, dict) and isinstance(inference.get("text"), str):
        generated_numbers |= numbers(inference["text"])
    unexplained = generated_numbers - numbers(input_text)
    if unexplained:
        errors.append("numbers absent from input: " + ", ".join(sorted(unexplained)))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a job reality card")
    parser.add_argument("card", type=Path)
    args = parser.parse_args()
    data = json.loads(args.card.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": "valid", "errors": []}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
