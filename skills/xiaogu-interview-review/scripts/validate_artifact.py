#!/usr/bin/env python3
"""Validate evidence links in Xiaogu resume and interview-review JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def validate_resume(payload: dict[str, Any]) -> list[str]:
    errors = []
    bullets = payload.get("bullets")
    if not isinstance(bullets, list) or not bullets:
        return ["resume must contain a non-empty bullets list"]
    for index, bullet in enumerate(bullets, 1):
        if not isinstance(bullet, dict):
            errors.append(f"bullet {index} must be an object")
            continue
        if not str(bullet.get("text", "")).strip():
            errors.append(f"bullet {index} missing text")
        evidence = bullet.get("evidence_ids")
        if not isinstance(evidence, list) or not evidence or not all(str(item).strip() for item in evidence):
            errors.append(f"bullet {index} must cite at least one evidence_id")
        if bullet.get("verification_status") not in {"confirmed", "needs_confirmation"}:
            errors.append(f"bullet {index} has invalid verification_status")
    return errors


def validate_review(payload: dict[str, Any]) -> list[str]:
    errors = []
    turns = payload.get("question_reviews")
    if not isinstance(turns, list) or not turns:
        return ["review must contain a non-empty question_reviews list"]
    for index, item in enumerate(turns, 1):
        if not isinstance(item, dict):
            errors.append(f"question_review {index} must be an object")
            continue
        quote = item.get("source_quote")
        if not isinstance(quote, dict) or not str(quote.get("text", "")).strip():
            errors.append(f"question_review {index} missing source_quote.text")
        if not str(item.get("diagnosis", "")).strip():
            errors.append(f"question_review {index} missing diagnosis")
        if item.get("fact_status") not in {"transcript_fact", "candidate_confirmed", "inference", "unknown"}:
            errors.append(f"question_review {index} has invalid fact_status")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("resume", "review"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate_resume(payload) if args.kind == "resume" else validate_review(payload)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
