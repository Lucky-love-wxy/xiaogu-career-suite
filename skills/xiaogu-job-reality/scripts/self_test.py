#!/usr/bin/env python3
"""Behavior checks for occupation recall, fallback, provenance, and validation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from analyze_job import analyze
from search_occupations import search
from validate_card import validate


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    exact = search("什么是算法工程师", limit=1)
    check(exact["matches"][0]["occupation"]["id"] == "algorithm-engineer", "generic algorithm exact match")
    check(exact["matches"][0]["confidence"] == "high", "exact title confidence")

    alias = search("固件工程师，负责设备驱动和烧录", limit=1)
    check(alias["matches"][0]["occupation"]["id"] == "embedded-software-engineer", "alias match")
    check(alias["matches"][0]["confidence"] == "high", "alias confidence")

    ambiguous = search("负责数据处理", limit=3)
    check(ambiguous["status"] == "index_miss", "single generic keyword must fail closed")

    missing = analyze("宠物营养师，负责犬猫膳食方案，月薪20K，双休")
    check(missing["match"]["status"] == "index_miss", "unknown occupation fallback")
    check("occupation_baseline" in missing["card"]["unknown_fields"], "unknown baseline is explicit")
    check(missing["card"]["jd_facts"], "index miss preserves literal JD facts")
    check("compensation" not in missing["card"]["unknown_fields"], "disclosed pay is not unknown")
    check("working_hours" not in missing["card"]["unknown_fields"], "disclosed hours are not unknown")

    jd = """推荐算法工程师
负责推荐模型训练和线上实验。
核心指标为点击率和转化率。
需要跨部门协作。"""
    card = analyze(jd)
    check(card["match"]["selected"]["id"] == "recommendation-algorithm-engineer", "specific child occupation wins")
    check([node["id"] for node in card["match"]["selected"]["hierarchy"]] == ["engineer", "algorithm-engineer", "recommendation-algorithm-engineer"], "hierarchy is resolved")
    check(all(item["status"] == "jd_fact" for item in card["card"]["jd_facts"]), "JD facts are labelled")
    check(not validate(card), "generated card validates")

    conflict = analyze("算法工程师，双休，但项目执行大小周，需要跨部门协作")
    check(conflict["card"]["conflicts"], "explicit JD conflict is surfaced")

    tampered = json.loads(json.dumps(card, ensure_ascii=False))
    tampered["card"]["jd_facts"][0]["text"] = "月薪50K"
    errors = validate(tampered)
    check(any("not a verbatim input" in error for error in errors), "fabricated JD fact is rejected")
    check(any("numbers absent from input" in error for error in errors), "fabricated number is rejected")

    forged_reference = json.loads(json.dumps(card, ensure_ascii=False))
    forged_reference["card"]["daily_work"][0]["text"] = "每天处理9999条"
    check(any("reference text is absent" in error for error in validate(forged_reference)), "forged reference is rejected")

    empty_fact = json.loads(json.dumps(card, ensure_ascii=False))
    empty_fact["card"]["jd_facts"][0]["text"] = ""
    check(any("jd_fact is empty" in error for error in validate(empty_fact)), "empty fact is rejected")

    index_conflict = analyze("算法工程师，不涉及模型部署，负责模型训练")
    check(any(item["source"] == "input+occupation_index" for item in index_conflict["card"]["conflicts"]), "JD-index conflict is surfaced")

    explicit_nonparticipation = analyze("算法工程师，明确不参与模型部署，负责模型训练")
    check(any(item["source"] == "input+occupation_index" for item in explicit_nonparticipation["card"]["conflicts"]), "explicit non-participation conflict is surfaced")

    prefixed_request = analyze("请帮我分析：算法工程师，负责模型训练和线上实验。")
    check(prefixed_request["card"]["jd_facts"], "request prefix does not discard ordinary duties")

    bad_type = json.loads(json.dumps(card, ensure_ascii=False))
    bad_type["card"]["questions"] = None
    check("questions must be a list" in validate(bad_type), "invalid list type returns an error")

    bad_selected = json.loads(json.dumps(card, ensure_ascii=False))
    bad_selected["match"]["selected"] = "algorithm-engineer"
    check("match.selected must be an object or null" in validate(bad_selected), "invalid selected type returns an error")

    check("root must be an object" in validate([]), "invalid root type returns an error")

    null_fact = json.loads(json.dumps(card, ensure_ascii=False))
    null_fact["card"]["jd_facts"][0]["text"] = None
    check("jd_facts statement text must be a string" in validate(null_fact), "null fact text returns an error")

    null_inference = json.loads(json.dumps(card, ensure_ascii=False))
    null_inference["card"]["occupation_inference"]["text"] = None
    check("occupation_inference text must be a string" in validate(null_inference), "null inference text returns an error")

    suffix_guard = json.loads(json.dumps(card, ensure_ascii=False))
    suffix_guard["input"]["text"] += "，团队20人"
    suffix_guard["card"]["jd_facts"][0]["text"] = "月薪20K"
    suffix_errors = validate(suffix_guard)
    check(any("numbers absent from input: 20K" in error for error in suffix_errors), "numeric suffixes are distinguished")

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "card.json"
        output.write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")
        check(output.exists(), "card can be persisted")
    print("self-test: 26 behavior checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
