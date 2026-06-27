from fastapi.testclient import TestClient

from skillsmarket.api import app


client = TestClient(app)


def test_persona_endpoint_returns_career_index_and_recommendations():
    response = client.get("/api/personas/mdm-lim")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "mdm-lim"
    assert body["career_index"]["index"] < 100
    assert body["recommendations"]
    assert body["target_role"]


def test_simulate_trade_endpoint_returns_before_after_delta():
    response = client.post("/api/simulate-trade", json={"persona_id": "mdm-lim", "target_skill": "Data Storytelling"})

    assert response.status_code == 200
    body = response.json()
    assert body["after_index"] > body["before_index"]
    assert body["delta"] > 0
    assert body["course"]["mapped_skill"] == "Data Storytelling"
    assert body["provenance"]


def test_shock_endpoint_preserves_divisor_and_exposes_changed_skills():
    before = client.get("/api/market/skills").json()
    response = client.post("/api/shocks/genai")

    assert response.status_code == 200
    body = response.json()
    assert body["divisor"] == before["divisor"]
    assert body["shock"]["name"] == "genai"
    assert body["changed_skills"]


def test_explain_endpoint_is_grounded_in_engine_output():
    response = client.get("/api/explain/skill/microsoft-excel")

    assert response.status_code == 200
    body = response.json()
    assert body["skill"] == "Microsoft Excel"
    assert body["source_rows"] >= 1
    assert body["formula"]


def test_llm_explain_rejects_missing_structured_facts():
    response = client.post("/api/explain/llm", json={})

    assert response.status_code == 422


def test_snapshot_and_ingest_endpoints_are_present_in_demo_mode():
    snapshots = client.get("/api/snapshots")
    assert snapshots.status_code == 200
    assert snapshots.json()["active_snapshot"]["kind"] == "fixture"

    ingest = client.post("/api/ingest/mycareersfuture", json={"pages": 0})
    assert ingest.status_code == 200
    assert ingest.json()["mode"] == "demo-fixture"

    recompute = client.post("/api/index/recompute", json={"snapshot_id": ingest.json()["active_snapshot"]["snapshot_id"]})
    assert recompute.status_code == 200
    assert recompute.json()["snapshot"]["kind"] == "fixture"


def test_market_skills_include_required_board_columns():
    response = client.get("/api/market/skills")

    assert response.status_code == 200
    skill = response.json()["skills"][0]
    assert {"symbol", "name", "price", "change", "demand", "supply_proxy", "sector", "provenance"} <= set(skill)
