#!/usr/bin/env python3
"""Read boss-agent-cli JSON envelopes and emit Xiaogu JobDocument records."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(value: Any, path: str) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path == "-":
        sys.stdout.write(payload)
    else:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")


def first(mapping: dict[str, Any], *names: str, default: Any = "") -> Any:
    for name in names:
        value = mapping.get(name)
        if value not in (None, ""):
            return value
    return default


def extract_items(envelope: Any) -> list[dict[str, Any]]:
    if isinstance(envelope, list):
        return [item for item in envelope if isinstance(item, dict)]
    if not isinstance(envelope, dict):
        raise ValueError("boss output must be a JSON object or list")
    if envelope.get("ok") is False:
        error = envelope.get("error") or {}
        code = error.get("code", "BOSS_ERROR")
        action = error.get("recovery_action") or error.get("hint") or "运行 boss doctor 检查"
        raise RuntimeError(f"{code}: {error.get('message', 'boss-agent-cli failed')} | {action}")
    data = envelope.get("data", envelope)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("jobs", "items", "jobList", "list", "result"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    return []


def normalize(item: dict[str, Any], *, source: str = "boss-agent-cli") -> dict[str, Any]:
    company_info = item.get("company_info") if isinstance(item.get("company_info"), dict) else {}
    title = str(first(item, "title", "job_name", "jobName"))
    company = str(first(item, "company", "brand_name", "brandName"))
    job_id = str(first(item, "job_id", "encrypt_job_id", "encryptJobId"))
    security_id = str(first(item, "security_id", "securityId"))
    raw_text = str(first(item, "description", "job_detail", "jobDetail"))
    stable_seed = "|".join((source, job_id, company, title, raw_text[:500]))
    stable_id = "job_" + hashlib.sha256(stable_seed.encode("utf-8")).hexdigest()[:16]
    return {
        "schema_version": "1.0",
        "id": stable_id,
        "source": source,
        "source_ref": {
            "job_id": job_id,
            "security_id": security_id,
            "lid": str(first(item, "lid")),
        },
        "retrieved_at": now_iso(),
        "position": {
            "title": title,
            "company": company,
            "salary": str(first(item, "salary", "salary_desc", "salaryDesc")),
            "city": str(first(item, "city", "city_name", "cityName")),
            "district": str(first(item, "district", "areaDistrict")),
            "experience": str(first(item, "experience", "jobExperience", "experienceName")),
            "education": str(first(item, "education", "jobDegree", "degreeName")),
            "employment_type": str(first(item, "employment_type")),
            "days_per_week": str(first(item, "days_per_week", "daysPerWeekDesc")),
            "least_month": str(first(item, "least_month", "leastMonthDesc")),
        },
        "company": {
            "industry": str(first(item, "industry", default=company_info.get("industry", ""))),
            "scale": str(first(item, "scale", default=company_info.get("scale", ""))),
            "stage": str(first(item, "stage", default=company_info.get("stage", ""))),
        },
        "skills": first(item, "skills", default=[]),
        "welfare": first(item, "welfare", "welfareList", default=[]),
        "full_text": raw_text,
        "source_snapshot": item,
        "status": "collected",
    }


def run_boss(arguments: list[str], boss_bin: str, timeout: int) -> Any:
    executable = shutil.which(boss_bin)
    if not executable:
        raise RuntimeError(
            "BOSS_CLI_MISSING: 未找到 boss-agent-cli。安装命令：uv tool install boss-agent-cli"
        )
    command = [executable, "--json", *arguments]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    raw = completed.stdout.strip() or completed.stderr.strip()
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"BOSS_OUTPUT_INVALID: boss did not return JSON: {raw[:300]}") from exc
    if completed.returncode != 0 and not (isinstance(envelope, dict) and envelope.get("ok") is False):
        raise RuntimeError(f"BOSS_EXIT_{completed.returncode}: {raw[:300]}")
    return envelope


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boss-bin", default="boss")
    parser.add_argument("--timeout", type=int, default=60)
    sub = parser.add_subparsers(dest="command", required=True)

    normal = sub.add_parser("normalize", help="normalize a saved boss JSON envelope")
    normal.add_argument("--input", required=True)
    normal.add_argument("--output", default="-")

    search = sub.add_parser("search", help="run a read-only boss search")
    search.add_argument("query")
    search.add_argument("--city")
    search.add_argument("--salary")
    search.add_argument("--experience")
    search.add_argument("--education")
    search.add_argument("--industry")
    search.add_argument("--welfare")
    search.add_argument("--output", default="-")

    detail = sub.add_parser("detail", help="read one job detail")
    detail.add_argument("security_id")
    detail.add_argument("--job-id")
    detail.add_argument("--output", default="-")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "normalize":
            envelope = load_json(args.input)
            documents = [normalize(item) for item in extract_items(envelope)]
            write_json({"ok": True, "jobs": documents}, args.output)
            return 0

        if args.command == "search":
            command = ["search", args.query]
            for flag, value in (
                ("--city", args.city), ("--salary", args.salary),
                ("--experience", args.experience), ("--education", args.education),
                ("--industry", args.industry), ("--welfare", args.welfare),
            ):
                if value:
                    command.extend((flag, value))
            envelope = run_boss(command, args.boss_bin, args.timeout)
            documents = [normalize(item) for item in extract_items(envelope)]
            write_json({"ok": True, "jobs": documents, "upstream": {"count": len(documents)}}, args.output)
            return 0

        command = ["detail", args.security_id]
        if args.job_id:
            command.extend(("--job-id", args.job_id))
        envelope = run_boss(command, args.boss_bin, args.timeout)
        documents = [normalize(item) for item in extract_items(envelope)]
        write_json({"ok": True, "jobs": documents}, args.output)
        return 0
    except (ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        write_json({"ok": False, "error": {"message": str(exc)}}, "-")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
