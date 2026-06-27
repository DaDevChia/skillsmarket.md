from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.history import seeded_history, sparkline

client = TestClient(app)


def test_seeded_history_anchors_to_current_price():
    history = seeded_history("Python", 142.0, days=90)
    assert len(history) == 90
    assert history[-1]["price"] == 142.0
    assert history[-1]["day"] == 0
    assert all(point["price"] > 0 for point in history)


def test_sparkline_is_short_and_ends_at_price():
    spark = sparkline("Data Analysis", 200.0)
    assert 10 <= len(spark) <= 20
    assert spark[-1] == 200.0


def test_market_skills_carry_sparkline_and_badges():
    skill = client.get("/api/market/skills").json()["skills"][0]
    assert skill["spark"]
    assert isinstance(skill["change_30d"], (int, float))
    assert skill["source_badges"]


def test_skill_detail_explains_methodology_and_history():
    response = client.get("/api/skill/microsoft-excel")
    assert response.status_code == 200
    body = response.json()
    assert body["skill"]["name"] == "Microsoft Excel"
    assert len(body["history"]) == 90
    assert "seeded historical proxy" in body["history_label"].lower()
    method = body["methodology"]
    for key in ("weighted_demand", "supply_proxy", "support", "divisor", "baseline", "formula"):
        assert key in method
    assert body["confidence"]["level"] in {"low", "medium", "high"}
    assert body["confidence"]["limitations"]
    assert body["source_badges"]
    assert body["analyst_note"]
    assert {"high", "low", "change_30d", "change_90d", "trend"} <= set(body["stats"])


def test_skill_detail_404_for_unknown():
    assert client.get("/api/skill/does-not-exist").status_code == 404


def test_catalogue_skill_detail_works():
    response = client.get("/api/skill/machine-learning")
    assert response.status_code == 200
    assert response.json()["skill"]["name"] == "Machine Learning"


def test_manual_skills_analysis_produces_index_and_actions():
    response = client.post("/api/resume/analyze-skills", json={"skills": ["Python", "Microsoft Excel", "SQL"]})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "manual"
    assert body["personal_index"] > 0
    assert body["actions"]
    assert body["highlights"]  # the synthesised text still yields linked evidence
    assert any(skill["name"] == "Python" for skill in body["skills"])


def test_manual_skills_rejects_empty():
    assert client.post("/api/resume/analyze-skills", json={"skills": []}).status_code == 422


def test_linkedin_is_labelled_not_ingested():
    sources = client.get("/api/market/summary").json()["data_sources"]
    linkedin = next(source for source in sources if source["name"] == "LinkedIn")
    assert linkedin["status"] == "not_currently_ingested"
