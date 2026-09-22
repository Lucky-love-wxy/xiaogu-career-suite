#!/usr/bin/env python3
"""Create and update the local Xiaogu career workspace."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_TRANSITIONS = {
    "collected": {"reviewing", "closed"},
    "reviewing": {"shortlisted", "closed"},
    "shortlisted": {"resume_ready", "closed"},
    "resume_ready": {"applied", "closed"},
    "applied": {"interview", "rejected", "withdrawn", "offer"},
    "interview": {"interview", "rejected", "withdrawn", "offer"},
    "offer": {"accepted", "declined"},
    "rejected": set(), "withdrawn": set(), "accepted": set(), "declined": set(), "closed": set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def state_path(root: Path) -> Path:
    return root / "_workspace" / "state.json"


def load_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    if not path.exists():
        raise RuntimeError(f"workspace not initialized: {root}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def init_workspace(root: Path) -> None:
    for relative in (
        "profile", "jobs/raw", "jobs/decoded", "resumes", "applications",
        "interviews/transcripts", "interviews/reviews", "knowledge/cards", "actions", "_workspace",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    path = state_path(root)
    if not path.exists():
        save_state(root, {
            "schema_version": "1.0",
            "created_at": now_iso(),
            "active_job_id": None,
            "jobs": {},
            "events": [],
        })
    profile = root / "profile" / "candidate-profile.md"
    if not profile.exists():
        profile.write_text(
            "# 候选人事实主档\n\n"
            "> 只记录本人确认的事实。待核实内容放在单独的待确认段，不写成既成经历。\n\n"
            "## 求职偏好\n\n## 经历索引\n\n## 技能与证据\n\n## 待确认\n",
            encoding="utf-8",
        )


def import_job(root: Path, source: Path) -> dict[str, Any]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list) or not jobs:
        raise RuntimeError("input must contain at least one normalized job")
    state = load_state(root)
    imported = []
    for job in jobs:
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError("normalized job missing id")
        target = root / "jobs" / "raw" / f"{job_id}.json"
        target.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        existing = state["jobs"].get(job_id, {})
        state["jobs"][job_id] = {
            **existing,
            "status": existing.get("status", "collected"),
            "title": job.get("position", {}).get("title", ""),
            "company": job.get("position", {}).get("company", ""),
            "job_document": str(target.relative_to(root)),
            "updated_at": now_iso(),
        }
        imported.append(job_id)
    state["events"].append({"at": now_iso(), "type": "jobs_imported", "job_ids": imported})
    save_state(root, state)
    return {"imported": imported}


def transition(root: Path, job_id: str, to_status: str, artifact: str | None) -> None:
    state = load_state(root)
    if job_id not in state["jobs"]:
        raise RuntimeError(f"unknown job id: {job_id}")
    current = state["jobs"][job_id]["status"]
    if to_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise RuntimeError(f"invalid transition: {current} -> {to_status}")
    state["jobs"][job_id]["status"] = to_status
    state["jobs"][job_id]["updated_at"] = now_iso()
    if artifact:
        artifacts = state["jobs"][job_id].setdefault("artifacts", [])
        if artifact not in artifacts:
            artifacts.append(artifact)
    state["active_job_id"] = job_id
    state["events"].append({"at": now_iso(), "type": "transition", "job_id": job_id, "from": current, "to": to_status, "artifact": artifact})
    save_state(root, state)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    imp = sub.add_parser("import-jobs")
    imp.add_argument("--input", required=True, type=Path)
    move = sub.add_parser("transition")
    move.add_argument("job_id")
    move.add_argument("to_status", choices=sorted(ALLOWED_TRANSITIONS))
    move.add_argument("--artifact")
    sub.add_parser("status")
    args = parser.parse_args()
    try:
        if args.command == "init":
            init_workspace(args.workspace)
            result: Any = {"initialized": str(args.workspace)}
        elif args.command == "import-jobs":
            result = import_job(args.workspace, args.input)
        elif args.command == "transition":
            transition(args.workspace, args.job_id, args.to_status, args.artifact)
            result = {"job_id": args.job_id, "status": args.to_status}
        else:
            result = load_state(args.workspace)
        print(json.dumps({"ok": True, "data": result}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": {"message": str(exc)}}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
