#!/usr/bin/env python3
"""Validate the Xiaogu jargon database before packaging."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_TEXT = (
    "term",
    "literal",
    "blunt",
    "hypothesis",
    "worst_case",
    "verify",
    "good_answer",
    "evidence_boundary",
)


def validate(rows: object) -> list[str]:
    if not isinstance(rows, list):
        return ["root must be a list"]
    errors: list[str] = []
    terms: set[str] = set()
    for index, row in enumerate(rows):
        label = f"entry[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        term = row.get("term")
        if isinstance(term, str) and term:
            if term in terms:
                errors.append(f"duplicate term: {term}")
            terms.add(term)
            label = term
        for field in REQUIRED_TEXT:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"{label}: missing text field {field}")
        for field in ("aliases", "red_flags", "fields"):
            value = row.get(field, [])
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{label}: {field} must be a string list")
        if len(row.get("red_flags", [])) < 2:
            errors.append(f"{label}: needs at least two observable red flags")
        if row.get("worst_case") == row.get("literal"):
            errors.append(f"{label}: worst_case must add a concrete risk")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path("database/jargon.json"))
    args = parser.parse_args()
    rows = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate(rows)
    print(json.dumps({"status": "valid" if not errors else "invalid", "count": len(rows), "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
