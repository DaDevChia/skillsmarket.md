"""Apify secondary-validation ingestion.

Apify is ingestion/automation infrastructure — it runs crawlers over private job
boards (JobStreet/JobsDB, Indeed, Google Jobs) to triangulate demand and
salary/job-money signals. It is NOT the original labour-market source and never
sets the index price. Built for a comprehensive sweep; on the FREE plan a real
run consumes limited credits, so the live sweep is gated and bounded.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from skillsmarket.apify_sources import actor_for_source
from skillsmarket.settings import settings


def _num(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").replace("$", "").split()[0])
    except (TypeError, ValueError, IndexError):
        return None


def normalize_apify_item(item: dict[str, Any], source: str) -> dict[str, Any]:
    """Best-effort normalise a scraped job listing to a common shape.

    Apify actors return heterogeneous schemas; we extract what corroborates
    demand and salary. Provenance is always ``apify`` (secondary validation).
    """
    salary_min = _num(item.get("salaryMin") or item.get("salary_from") or (item.get("salary") or {}).get("min"))
    salary_max = _num(item.get("salaryMax") or item.get("salary_to") or (item.get("salary") or {}).get("max"))
    return {
        "id": str(item.get("id") or item.get("jobId") or item.get("url") or "unknown"),
        "title": str(item.get("title") or item.get("jobTitle") or item.get("position") or "Untitled role"),
        "company": item.get("company") or item.get("companyName"),
        "location": item.get("location") or item.get("jobLocation"),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "url": item.get("url") or item.get("jobUrl"),
        "source": source,
        "provenance": "apify",
    }


def fetch_dataset_items(dataset_id: str, limit: int = 100) -> list[dict[str, Any]]:
    if not settings.apify_token:
        raise RuntimeError("APIFY_TOKEN is not configured")
    url = f"https://api.apify.com/v2/datasets/{quote(dataset_id, safe='')}/items"
    with httpx.Client(timeout=60) as client:
        response = client.get(url, params={"token": settings.apify_token, "limit": limit, "clean": "true"})
        response.raise_for_status()
        return response.json()


def run_actor_and_fetch(
    source: str,
    keyword: str = "data analyst",
    location: str = "Singapore",
    max_items: int = 30,
    wait_for_finish: int = 60,
) -> dict[str, Any]:
    """Run a configured actor synchronously and fetch + normalise its dataset.

    Bounded by ``max_items`` to stay within free credits. For a comprehensive
    multi-board sweep, raise max_items and call across sources on a paid plan.
    """
    actor = actor_for_source(source)
    if not settings.apify_token:
        raise RuntimeError("APIFY_TOKEN is not configured")
    actor_input = {"keyword": keyword, "location": location, "maxItems": max_items}
    run_url = f"https://api.apify.com/v2/acts/{quote(actor, safe='')}/runs"
    params = {"token": settings.apify_token, "waitForFinish": wait_for_finish}
    with httpx.Client(timeout=max(30, wait_for_finish + 20)) as client:
        run = client.post(run_url, params=params, json=actor_input)
        run.raise_for_status()
        data = run.json().get("data", {})
        dataset_id = data.get("defaultDatasetId")
        items = fetch_dataset_items(dataset_id, limit=max_items) if dataset_id else []
    normalised = [normalize_apify_item(item, source) for item in items]
    return {
        "source": source,
        "actor": actor,
        "status": data.get("status"),
        "dataset_id": dataset_id,
        "record_count": len(normalised),
        "records": normalised,
        "note": "Secondary validation via Apify (ingestion infrastructure); never sets the index price.",
    }
