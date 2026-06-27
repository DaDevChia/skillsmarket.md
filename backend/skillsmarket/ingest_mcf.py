"""Live MyCareersFuture sweep.

Pulls real job postings from the MyCareersFuture public search API across a
spread of Singapore-relevant queries, dedupes by job UUID, normalises, and
writes a real snapshot. The resulting market is provenance ``real_proxy`` —
every skill traces to real job UUIDs you can open on mycareersfuture.gov.sg.
"""

from __future__ import annotations

from typing import Any

import httpx

from skillsmarket.ingest import normalize_mycareersfuture_job, write_snapshot

MCF_SEARCH_URL = "https://api.mycareersfuture.gov.sg/v2/search"
MCF_JOB_URL = "https://www.mycareersfuture.gov.sg/job"

# Broad coverage across the domains the skill universe spans.
DEFAULT_QUERIES = [
    "data analyst", "software engineer", "cloud engineer", "cybersecurity",
    "accountant", "human resources", "logistics", "supply chain", "marketing",
    "operations", "administrative executive", "project manager", "nurse",
    "machine learning", "devops", "finance analyst", "business analyst",
    "sustainability", "customer service", "sales",
]


def mcf_search(query: str, page: int = 0, limit: int = 30, client: httpx.Client | None = None) -> list[dict[str, Any]]:
    owns = client is None
    client = client or httpx.Client(timeout=30)
    try:
        response = client.post(
            MCF_SEARCH_URL,
            params={"limit": limit, "page": page},
            json={"search": query, "sessionId": ""},
        )
        response.raise_for_status()
        return response.json().get("results") or []
    finally:
        if owns:
            client.close()


def sweep_mycareersfuture(
    queries: list[str] | None = None,
    pages: int = 2,
    limit: int = 30,
) -> list[dict[str, Any]]:
    """Aggregate + dedupe normalised postings across many queries."""
    queries = queries or DEFAULT_QUERIES
    seen: dict[str, dict[str, Any]] = {}
    with httpx.Client(timeout=30) as client:
        for query in queries:
            for page in range(pages):
                try:
                    raw_results = mcf_search(query, page=page, limit=limit, client=client)
                except httpx.HTTPError:
                    break
                if not raw_results:
                    break
                for raw in raw_results:
                    record = normalize_mycareersfuture_job(raw)
                    if record["id"] and record["id"] != "unknown" and record["id"] not in seen:
                        record["job_url"] = f"{MCF_JOB_URL}/{record['id']}"
                        record["query"] = query
                        seen[record["id"]] = record
    return list(seen.values())


def run_live_snapshot(pages: int = 2, limit: int = 30) -> dict[str, Any]:
    """Run a sweep and persist it as a real direct-public-api snapshot."""
    records = sweep_mycareersfuture(pages=pages, limit=limit)
    snapshot = write_snapshot(records, {"sweep": True, "source": "mycareersfuture_search"}, kind="direct-public-api")
    return {"mode": "live-sweep", "active_snapshot": snapshot, "record_count": len(records)}
