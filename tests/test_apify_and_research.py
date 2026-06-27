from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.ingest_apify import normalize_apify_item

client = TestClient(app)


def test_normalize_apify_item_labels_provenance_apify():
    item = {"title": "Data Analyst", "companyName": "Acme", "salaryMin": "4,000", "salaryMax": "6000", "url": "https://x/y"}
    out = normalize_apify_item(item, "jobstreet")
    assert out["provenance"] == "apify"
    assert out["source"] == "jobstreet"
    assert out["title"] == "Data Analyst"
    assert out["salary_min"] == 4000.0
    assert out["salary_max"] == 6000.0


def test_research_known_skill_returns_market_quote():
    response = client.post("/api/skill/research", json={"name": "Microsoft Excel"})
    assert response.status_code == 200
    body = response.json()
    assert body["on_market"] is True
    assert body["skill_id"] == "microsoft-excel"
    assert "courses" in body


def test_research_unknown_skill_is_labelled_and_fails_closed():
    # Research is opt-in; with it disabled (test default) we get a clear, honest null.
    response = client.post("/api/skill/research", json={"name": "Quantum Underwater Basket Weaving"})
    assert response.status_code == 200
    body = response.json()
    assert body["on_market"] is False
    assert body["research"] is None  # fails closed when research disabled / no key
    assert body["research_enabled"] is False
