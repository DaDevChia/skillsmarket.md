from fastapi.testclient import TestClient

from skillsmarket.api import app


def test_market_summary_has_dashboard_fields():
    client = TestClient(app)
    response = client.get("/api/market/summary")

    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"skills", "sectors", "persona", "provenance", "recommendations"}
    assert body["provenance"][0]["status"] in {"real", "real_proxy", "curated_demo", "seeded"}
