from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

import httpx

from skillsmarket.fixtures import active_snapshot, demo_postings

MCF_JOBS_URL = "https://api.mycareersfuture.gov.sg/v2/jobs"
SNAPSHOT_DIR = Path("data/raw/mycareersfuture")


def _first_name(items: list[dict[str, Any]] | None, default: str = "Unclassified") -> str:
    if not items:
        return default
    first = items[0]
    return str(first.get("category") or first.get("name") or first.get("label") or first.get("id") or default)


def normalize_mycareersfuture_job(raw: dict[str, Any], key_top_n: int = 5) -> dict[str, Any]:
    metadata = raw.get("metadata") or {}
    salary = raw.get("salary") or {}
    skills = []
    for index, skill in enumerate(raw.get("skills") or []):
        name = skill.get("skill") or skill.get("name") or skill.get("title")
        if not name:
            continue
        # Respect isKeySkill when present; the search API omits it, so fall back to
        # a position heuristic (leading skills ≈ key, documented).
        raw_key = skill.get("isKeySkill")
        if raw_key is None:
            raw_key = skill.get("is_key")
        is_key = bool(raw_key) if raw_key is not None else index < key_top_n
        skills.append(
            {
                "id": str(skill.get("uuid") or skill.get("id") or name).strip(),
                "name": str(name).strip(),
                "is_key": is_key,
            }
        )

    return {
        "id": str(raw.get("uuid") or raw.get("job_id") or raw.get("jobPostId") or raw.get("id") or "unknown"),
        "title": str(raw.get("title") or raw.get("jobTitle") or "Untitled role"),
        "applications": int(metadata.get("totalNumberJobApplication") or raw.get("applications") or 1),
        "views": int(metadata.get("totalNumberOfView") or 0),
        "sector": _first_name(raw.get("categories")),
        "position_level": _first_name(raw.get("positionLevels"), default="Unknown"),
        "salary_min": salary.get("minimum"),
        "salary_max": salary.get("maximum"),
        "ssoc_code": raw.get("ssocCode"),
        "posted_at": metadata.get("newPostingDate") or raw.get("newPostingDate"),
        "expiry_date": raw.get("expiryDate"),
        "source": "MyCareersFuture",
        "skills": skills,
    }


def write_snapshot(records: list[dict[str, Any]], raw_payload: dict[str, Any] | None = None, snapshot_id: str | None = None, kind: str = "direct-public-api") -> dict[str, Any]:
    snapshot_id = snapshot_id or datetime.now(timezone.utc).strftime("mcf-%Y%m%dT%H%M%SZ")
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    out = SNAPSHOT_DIR / f"{snapshot_id}.json"
    payload = {"snapshot_id": snapshot_id, "kind": kind, "records": records, "raw": raw_payload or {}, "created_at": datetime.now(timezone.utc).isoformat()}
    out.write_text(json.dumps(payload, indent=2))
    return {"snapshot_id": snapshot_id, "kind": kind, "path": str(out), "record_count": len(records), "created_at": payload["created_at"]}


def list_snapshots() -> list[dict[str, Any]]:
    snapshots = []
    if SNAPSHOT_DIR.exists():
        for path in sorted(SNAPSHOT_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text())
            except json.JSONDecodeError:
                continue
            snapshots.append(
                {
                    "snapshot_id": payload.get("snapshot_id") or path.stem,
                    "kind": payload.get("kind", "unknown"),
                    "path": str(path),
                    "record_count": len(payload.get("records") or []),
                    "created_at": payload.get("created_at"),
                }
            )
    if not snapshots:
        fixture = write_snapshot(demo_postings(), {"fixture": True}, snapshot_id="fixture-base-2026-06-24", kind="fixture")
        snapshots.append(fixture)
    return snapshots


def load_snapshot(snapshot_id: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    snapshots = list_snapshots()
    selected = next((row for row in snapshots if row["snapshot_id"] == snapshot_id), snapshots[0]) if snapshot_id else snapshots[0]
    payload = json.loads(Path(selected["path"]).read_text())
    return payload.get("records") or [], selected


def ingest_mycareersfuture(pages: int = 0, limit: int = 100) -> dict[str, Any]:
    """Ingest bounded MyCareersFuture pages. pages=0 uses deterministic demo fixture."""
    if pages <= 0:
        records = demo_postings()
        snapshot = write_snapshot(records, {"fixture": True}, snapshot_id="fixture-base-2026-06-24", kind="fixture")
        return {"mode": "demo-fixture", "active_snapshot": snapshot, "records": records, "record_count": len(records)}

    all_records: list[dict[str, Any]] = []
    raw_pages: list[dict[str, Any]] = []
    with httpx.Client(timeout=30) as client:
        for page in range(pages):
            response = client.get(MCF_JOBS_URL, params={"limit": limit, "page": page})
            response.raise_for_status()
            payload = response.json()
            raw_pages.append(payload)
            for raw in payload.get("results") or []:
                all_records.append(normalize_mycareersfuture_job(raw))
    snapshot = write_snapshot(all_records, {"pages": raw_pages}, kind="direct-public-api")
    return {"mode": "direct-public-api", "active_snapshot": snapshot, "records": all_records, "record_count": len(all_records)}
