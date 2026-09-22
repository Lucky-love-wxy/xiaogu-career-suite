#!/usr/bin/env python3
"""Search the bundled occupation reality index.

Usage:
  python3 scripts/search_occupations.py --query "推荐算法工程师 JD..."
  python3 scripts/search_occupations.py --file jd.txt --limit 3
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROJECT_INDEX = Path(__file__).resolve().parents[3] / "database" / "occupations.json"
BUNDLED_INDEX = SKILL_ROOT / "references" / "occupations.json"
INDEX = BUNDLED_INDEX if BUNDLED_INDEX.exists() else PROJECT_INDEX


def score(query: str, item: dict) -> dict:
    query_lower = query.lower()
    name_hit = item["name"].lower() in query_lower
    alias_hits = [term for term in item.get("aliases", []) if term.lower() in query_lower]
    keyword_hits = [term for term in item.get("keywords", []) if term.lower() in query_lower]
    hits = ([item["name"]] if name_hit else []) + alias_hits + keyword_hits
    total = 0
    if name_hit:
        total += 20
    total += len(alias_hits) * 14
    total += len(keyword_hits) * 3
    if name_hit or alias_hits:
        confidence = "high"
    elif len(keyword_hits) >= 2:
        confidence = "medium"
    elif len(keyword_hits) == 1:
        confidence = "low"
    else:
        confidence = "none"
    return {
        "score": total,
        "confidence": confidence,
        "matched_terms": hits,
        "name_hit": name_hit,
        "alias_hits": alias_hits,
        "keyword_hits": keyword_hits,
    }


def load_index() -> list[dict]:
    return json.loads(INDEX.read_text(encoding="utf-8"))


def search(query: str, limit: int = 3, include_low: bool = False) -> dict:
    ranked = []
    for item in load_index():
        match = score(query, item)
        if match["confidence"] == "none":
            continue
        if match["confidence"] == "low" and not include_low:
            continue
        ranked.append({**match, "occupation": item})
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    ranked.sort(key=lambda row: (confidence_order[row["confidence"]], -row["score"], row["occupation"]["name"]))
    return {
        "query": query,
        "match_count": len(ranked),
        "matches": ranked[: max(limit, 0)],
        "status": "matched" if ranked else "index_miss",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Xiaogu's occupation reality index")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query", help="Job title or full JD text")
    source.add_argument("--file", type=Path, help="UTF-8 text file containing a JD")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--include-low", action="store_true", help="Include unsafe single-keyword candidates")
    args = parser.parse_args()

    query = args.query if args.query is not None else args.file.read_text(encoding="utf-8")
    result = search(query, limit=args.limit, include_low=args.include_low)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
