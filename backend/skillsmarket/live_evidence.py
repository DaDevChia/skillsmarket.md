"""Real per-skill evidence + a live salary-priced market from MyCareersFuture.

Why salary-priced: the MCF search API returns applicant counts that are almost
always 0, so the demand/supply scarcity model degenerates (common skills float
to the top). Salary IS reliably present, so the *live* index prices each skill
on its real median monthly salary (median → 100). Demand (real posting count)
and sample real jobs ride along as evidence. Everything here is labelled
real_proxy and traceable to real MyCareersFuture job UUIDs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from skillsmarket.engine import _seeded_change, _skill_id, _symbol_for

EVIDENCE_PATH = Path("data/live_evidence.json")

# Map our catalogue names to the names MyCareersFuture actually uses.
EVIDENCE_ALIASES = {
    "amazon web services": "aws",
    "google cloud platform": "google cloud",
    "microsoft azure": "azure",
    "ci/cd pipelines": "ci/cd",
    "version control (git)": "git",
    "search engine optimisation": "seo",
    "big data (spark)": "apache spark",
    "workplace safety (wsh)": "workplace safety and health",
    "generative ai": "generative ai",
}


def _job_salary_mid(job: dict[str, Any]) -> float | None:
    lo, hi = job.get("salary_min"), job.get("salary_max")
    if lo and hi:
        return (float(lo) + float(hi)) / 2.0
    return None


def build_evidence_aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate real postings per skill name."""
    agg: dict[str, dict[str, Any]] = {}
    for job in records:
        salary_mid = _job_salary_mid(job)
        for skill in job.get("skills", []):
            name = str(skill.get("name", "")).strip()
            if not name:
                continue
            entry = agg.setdefault(
                name.lower(),
                {"name": name, "support": 0, "salaries": [], "applicants": [], "sectors": {}, "jobs": []},
            )
            entry["support"] += 1
            if salary_mid:
                entry["salaries"].append(salary_mid)
            entry["applicants"].append(max(int(job.get("applications") or 1), 1))
            sector = job.get("sector") or "Unclassified"
            entry["sectors"][sector] = entry["sectors"].get(sector, 0) + 1
            if len(entry["jobs"]) < 6:
                entry["jobs"].append(
                    {
                        "title": job.get("title"),
                        "uuid": job.get("id"),
                        "url": job.get("job_url"),
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "sector": sector,
                    }
                )
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "MyCareersFuture",
        "job_count": len(records),
        "skills": agg,
    }


def write_evidence(aggregate: dict[str, Any]) -> Path:
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(aggregate))
    return EVIDENCE_PATH


def load_evidence() -> dict[str, Any] | None:
    if not EVIDENCE_PATH.exists():
        return None
    try:
        return json.loads(EVIDENCE_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _summary_for(entry: dict[str, Any], fetched_at: str) -> dict[str, Any]:
    salaries = entry.get("salaries") or []
    return {
        "found": True,
        "source": "MyCareersFuture",
        "fetched_at": fetched_at,
        "demand": entry["support"],
        "salary_min": round(min(salaries)) if salaries else None,
        "salary_max": round(max(salaries)) if salaries else None,
        "salary_mid": round(median(salaries)) if salaries else None,
        "top_sector": max(entry["sectors"], key=entry["sectors"].get) if entry.get("sectors") else None,
        "sample_jobs": entry.get("jobs", [])[:5],
    }


def evidence_for_skill(name: str, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = evidence or load_evidence()
    if not evidence:
        return {"found": False}
    skills = evidence.get("skills", {})
    key = name.lower()
    entry = skills.get(key) or skills.get(EVIDENCE_ALIASES.get(key, key))
    if not entry:
        return {"found": False}
    return _summary_for(entry, evidence.get("fetched_at", ""))


_LIVE_CACHE: dict[str, Any] = {}


def latest_live_snapshot() -> Path | None:
    snapshot_dir = Path("data/raw/mycareersfuture")
    if not snapshot_dir.exists():
        return None
    live = sorted(snapshot_dir.glob("mcf-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return live[0] if live else None


def live_market_or_none() -> dict[str, Any] | None:
    """Compute (and memoise) the live salary-priced market from the newest snapshot."""
    path = latest_live_snapshot()
    if path is None:
        return None
    key = f"{path}:{path.stat().st_mtime_ns}"
    if _LIVE_CACHE.get("key") != key:
        try:
            records = json.loads(path.read_text()).get("records") or []
        except (json.JSONDecodeError, OSError):
            return None
        market = compute_live_market(records)
        market["snapshot_id"] = path.stem
        _LIVE_CACHE.clear()
        _LIVE_CACHE.update({"key": key, "market": market})
    return _LIVE_CACHE.get("market")


def compute_live_market(records: list[dict[str, Any]], min_support: int = 4) -> dict[str, Any]:
    """A live market priced on real median salary (median salary → 100)."""
    aggregate = build_evidence_aggregate(records)
    rows: list[dict[str, Any]] = []
    for entry in aggregate["skills"].values():
        if entry["support"] < min_support:
            continue
        salaries = entry.get("salaries") or []
        salary_mid = median(salaries) if salaries else None
        rows.append({"entry": entry, "salary_mid": salary_mid})

    priced_salaries = [row["salary_mid"] for row in rows if row["salary_mid"]]
    median_salary = median(priced_salaries) if priced_salaries else 1.0

    skills: list[dict[str, Any]] = []
    for row in rows:
        entry = row["entry"]
        salary_mid = row["salary_mid"]
        # Price on relative salary; demand-only skills sit at the baseline.
        price = round((salary_mid / median_salary) * 100, 2) if salary_mid else 100.0
        applicants = entry["applicants"]
        supply = round(sum(applicants) / len(applicants), 2) if applicants else 1.0
        sector = max(entry["sectors"], key=entry["sectors"].get) if entry.get("sectors") else "Unclassified"
        name = entry["name"]
        skills.append(
            {
                "id": _skill_id(name),
                "symbol": _symbol_for(name),
                "name": name,
                "sector": sector,
                "sectors": [{"name": sector, "weight": 1.0}],
                "price": price,
                "change": _seeded_change(name, price),
                "demand": entry["support"],
                "weighted_demand": entry["support"],
                "supply": supply,
                "supply_proxy": supply,
                "raw_score": round(salary_mid or 0.0, 2),
                "source_rows": [job["uuid"] for job in entry["jobs"] if job.get("uuid")],
                "source_row_count": entry["support"],
                "salary_mid": round(salary_mid, 2) if salary_mid else None,
                "salary_premium": round(salary_mid / median_salary, 2) if salary_mid else None,
                "is_soft_skill": False,
                "provenance": "real_proxy",
                "unit": "points",
            }
        )
    skills.sort(key=lambda skill: skill["price"], reverse=True)
    return {"baseline": 100.0, "divisor": round(median_salary, 4), "skills": skills, "sectors": []}
