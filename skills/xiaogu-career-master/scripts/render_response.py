#!/usr/bin/env python3
"""Validate and render a Xiaogu user-facing response from structured JSON.

Usage: python3 render_response.py response.json
Input: one JSON object following references/output-contract.md.
Output: concise Markdown on stdout; nonzero exit on invalid input.
Dependencies: Python standard library only. This command is read-only and idempotent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


STATUSES = {"complete", "needs_input", "blocked"}
EVIDENCE_KINDS = {
    "jd_fact", "offer_fact", "transcript_fact", "candidate_confirmed",
    "reference", "external_report", "inference",
}
LABELS = {
    "jd_fact": "JD 原文", "offer_fact": "Offer 原文",
    "transcript_fact": "面试原话", "candidate_confirmed": "本人确认",
    "reference": "参考资料", "external_report": "外部分享",
    "inference": "待核实推断",
}

INTERNAL = re.compile(r"primary_skill|missing_inputs|evidence_ids|_xiaogu-runtime|route_request\.py|render_response\.py|candidate_confirmed|transcript_fact|```(?:json|python|bash)", re.I)


def visible_text_error(value: str) -> bool:
    return bool(INTERNAL.search(value))


def validate(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["response must be an object"]
    errors: list[str] = []
    status = payload.get("status")
    if status not in STATUSES:
        errors.append("status must be complete, needs_input, or blocked")
    if status == "needs_input":
        if not isinstance(payload.get("question"), str) or not payload["question"].strip():
            errors.append("needs_input requires one question")
        elif "\n" in payload["question"] or len(payload["question"]) > 160 or len(re.findall(r"[？?]", payload["question"])) > 1 or visible_text_error(payload["question"]):
            errors.append("question must be one short, plain-language question")
        if payload.get("next_action"):
            errors.append("needs_input cannot add a second action")
        return errors
    for key in ("answer", "unknown"):
        value = payload.get(key)
        if key == "answer" and (not isinstance(value, str) or not value.strip()):
            errors.append("answer must be nonempty")
        if key == "unknown" and (not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value)):
            errors.append("unknown must be a string list")
    evidence = payload.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or item.get("kind") not in EVIDENCE_KINDS or not isinstance(item.get("text"), str) or not item["text"].strip():
                errors.append(f"evidence[{index}] requires kind and text")
    action = payload.get("next_action")
    if action is not None and (not isinstance(action, str) or not action.strip() or "\n" in action):
        errors.append("next_action must be one short line or null")
    if status == "blocked" and (not isinstance(payload.get("blocker"), str) or not payload["blocker"].strip()):
        errors.append("blocked requires blocker")
    if isinstance(payload.get("answer"), str) and len(payload["answer"]) > 1200:
        errors.append("answer too long; keep details in the saved artifact")
    for key in ("answer", "blocker", "next_action"):
        if isinstance(payload.get(key), str) and visible_text_error(payload[key]):
            errors.append(f"{key} exposes internal implementation fields")
    for text in payload.get("unknown", []) if isinstance(payload.get("unknown"), list) else []:
        if isinstance(text, str) and visible_text_error(text):
            errors.append("unknown exposes internal implementation fields")
    for item in evidence if isinstance(evidence, list) else []:
        if isinstance(item, dict) and isinstance(item.get("text"), str) and visible_text_error(item["text"]):
            errors.append("evidence exposes internal implementation fields")
    return errors


def render(payload: dict) -> str:
    errors = validate(payload)
    if errors:
        raise ValueError("; ".join(errors))
    if payload["status"] == "needs_input":
        return payload["question"].strip() + "\n"
    lines = [f"**结论** {payload['answer'].strip()}"]
    if payload["evidence"]:
        lines.extend(["", "**依据**"])
        for item in payload["evidence"]:
            lines.append(f"- {LABELS[item['kind']]}：{item['text'].strip()}")
    if payload["status"] == "blocked":
        lines.extend(["", f"**受阻原因** {payload['blocker'].strip()}"])
    if payload["unknown"]:
        lines.extend(["", "**仍需确认**"])
        lines.extend(f"- {item.strip()}" for item in payload["unknown"])
    if payload.get("next_action"):
        lines.extend(["", f"**下一步** {payload['next_action'].strip()}"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.path.read_text(encoding="utf-8"))
        sys.stdout.write(render(payload))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"invalid response: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
