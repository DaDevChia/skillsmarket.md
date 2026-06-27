from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.ingest import normalize_mycareersfuture_job
from skillsmarket.live_evidence import (
    build_evidence_aggregate,
    compute_live_market,
    evidence_for_skill,
)
from skillsmarket.skillsfuture import build_course_index, course_detail_url, courses_for_skill

client = TestClient(app)


def _sample_records():
    return [
        {"id": "job-a", "title": "Data Analyst", "applications": 0, "sector": "IT", "job_url": "u/a",
         "salary_min": 6000, "salary_max": 8000, "skills": [{"name": "Python", "is_key": True}, {"name": "SQL", "is_key": True}]},
        {"id": "job-b", "title": "ML Engineer", "applications": 0, "sector": "IT", "job_url": "u/b",
         "salary_min": 9000, "salary_max": 13000, "skills": [{"name": "Python", "is_key": True}, {"name": "Machine Learning", "is_key": True}]},
        {"id": "job-c", "title": "Admin", "applications": 0, "sector": "Admin", "job_url": "u/c",
         "salary_min": 2500, "salary_max": 3500, "skills": [{"name": "Microsoft Excel", "is_key": True}]},
    ]


def test_normalize_uses_category_and_key_heuristic():
    raw = {
        "uuid": "x", "title": "Engineer",
        "metadata": {"totalNumberJobApplication": 0},
        "salary": {"minimum": 5000, "maximum": 7000},
        "categories": [{"category": "Information Technology"}],
        "skills": [{"skill": "Python", "uuid": "p"}, {"skill": "Docker", "uuid": "d"}],
    }
    posting = normalize_mycareersfuture_job(raw)
    assert posting["sector"] == "Information Technology"
    # Search API omits isKeySkill -> leading skills treated as key.
    assert posting["skills"][0]["is_key"] is True


def test_compute_live_market_prices_on_salary():
    market = compute_live_market(_sample_records(), min_support=1)
    prices = {s["name"]: s["price"] for s in market["skills"]}
    assert market["skills"][0]["provenance"] == "real_proxy"
    # ML role pays most -> Machine Learning prices above Microsoft Excel.
    assert prices["Machine Learning"] > prices["Microsoft Excel"]
    # Real job UUIDs ride along as source rows.
    ml = next(s for s in market["skills"] if s["name"] == "Machine Learning")
    assert ml["source_rows"]


def test_evidence_aggregate_and_lookup():
    agg = build_evidence_aggregate(_sample_records())
    ev = evidence_for_skill("Python", agg)
    assert ev["found"] is True
    assert ev["demand"] == 2
    assert ev["salary_min"] and ev["salary_max"]
    assert ev["sample_jobs"][0]["url"]


def test_course_index_matches_titles_and_links():
    courses = [
        {"ref": "TGS-1", "title": "Python for Data", "provider": "Poly", "fee": 900, "hours": 21, "learn": "pandas"},
        {"ref": "TGS-2", "title": "Welding Basics", "provider": "ITE", "fee": 300, "hours": 40, "learn": "metal"},
    ]
    index = build_course_index(["Python"], courses)
    result = courses_for_skill("Python", index)
    assert result["found"] is True
    assert result["matches"][0]["url"] == course_detail_url("TGS-1")


def test_skill_detail_exposes_evidence_and_course_keys():
    body = client.get("/api/skill/microsoft-excel").json()
    assert "live_evidence" in body
    assert "courses" in body
    assert isinstance(body["live_evidence"].get("found"), bool)
    assert isinstance(body["courses"].get("found"), bool)
