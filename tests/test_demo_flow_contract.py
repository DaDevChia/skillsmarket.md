from fastapi.testclient import TestClient

from skillsmarket.api import app


def test_three_minute_demo_flow_contract():
    client = TestClient(app)

    summary = client.get("/api/market/summary").json()
    assert summary["persona"]["career_index"]["index"] < 100

    explanation = client.get("/api/explain/skill/Microsoft%20Excel").json()
    assert explanation["source_rows"] >= 1

    trade = client.post("/api/simulate-trade", json={"persona_id": "mdm-lim", "target_skill": "Data Storytelling"}).json()
    assert trade["delta"] > 0

    shock = client.post("/api/shocks/genai").json()
    assert shock["shock"]["message"].startswith("Automation is modelled")
