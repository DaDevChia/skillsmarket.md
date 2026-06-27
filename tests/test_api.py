from fastapi.testclient import TestClient

from skillsmarket.api import app


def test_health_endpoint_reports_ok():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "skillsmarket"}


def test_market_skills_endpoint_returns_priced_skills():
    client = TestClient(app)

    response = client.get("/api/market/skills")

    assert response.status_code == 200
    body = response.json()
    assert body["baseline"] == 100.0
    assert body["skills"]
    assert all("price" in skill for skill in body["skills"])
