#!/usr/bin/env python3
"""Deterministic jargon and occupation lookup bundled with xiaogu-career-suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JARGON = ROOT / "references" / "jargon.json"
OCCUPATIONS = ROOT / "references" / "occupations.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def search_jargon(query: str) -> dict:
    rows = []
    lower = query.lower()
    for entry in load(JARGON):
        terms = [entry.get("term", ""), *entry.get("aliases", [])]
        hits = [term for term in terms if term and term.lower() in lower]
        if hits:
            rows.append({
                "id": entry.get("id", entry["term"]),
                "term": entry["term"],
                "matched_text": max(hits, key=len),
                "entry": entry,
                "source": "references/jargon.json",
                "confidence": "exact_or_alias",
            })
    rows.sort(key=lambda item: (-len(item["matched_text"]), item["term"]))
    return {"query": query, "type": "jargon", "status": "matched" if rows else "index_miss", "matches": rows}


def search_occupations(query: str, limit: int = 5) -> dict:
    lower = query.lower()
    rows = []
    for entry in load(OCCUPATIONS):
        name = entry["name"]
        aliases = entry.get("aliases", [])
        keywords = entry.get("keywords", [])
        name_hit = name.lower() in lower
        alias_hits = [term for term in aliases if term.lower() in lower]
        keyword_hits = [term for term in keywords if term.lower() in lower]
        score = (30 if name_hit else 0) + len(alias_hits) * 18 + len(keyword_hits) * 4
        if name_hit or alias_hits or len(keyword_hits) >= 2:
            rows.append({
                "id": entry["id"],
                "name": name,
                "score": score,
                "confidence": "high" if name_hit or alias_hits else "medium",
                "matched_terms": ([name] if name_hit else []) + alias_hits + keyword_hits,
                "occupation": entry,
                "source": "references/occupations.json",
            })
    rows.sort(key=lambda item: (-item["score"], item["name"]))
    return {"query": query, "type": "occupation", "status": "matched" if rows else "index_miss", "matches": rows[:max(0, limit)]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="kind", required=True)
    for name in ("jargon", "occupation", "analyze"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--query", required=True)
        subparser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if args.kind == "jargon":
        result = search_jargon(args.query)
    elif args.kind == "occupation":
        result = search_occupations(args.query, args.limit)
    else:
        result = {
            "query": args.query,
            "type": "analyze",
            "jargon": search_jargon(args.query),
            "occupation": search_occupations(args.query, args.limit),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
