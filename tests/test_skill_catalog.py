from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.skill_catalog import CATALOG, augment_market_with_catalog, build_catalog_skills

client = TestClient(app)


def test_catalogue_has_unique_names_and_ids():
    names = [name for name, _s, _t in CATALOG]
    assert len(names) == len(set(names))
    rows = build_catalog_skills(0.0004)
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))


def test_market_exposes_at_least_100_priced_skills():
    response = client.get("/api/market/skills")
    assert response.status_code == 200
    skills = response.json()["skills"]
    assert len(skills) >= 100
    # Every row must be priced and provenance-labelled (sortable + honest).
    for skill in skills:
        assert isinstance(skill["price"], (int, float))
        assert skill["provenance"] in {"seeded", "real_proxy", "real", "curated_demo"}
        assert {"symbol", "name", "sector", "change"} <= set(skill)


def test_catalogue_skills_are_seeded_and_span_domains():
    response = client.get("/api/market/skills")
    skills = response.json()["skills"]
    sectors = {skill["sector"] for skill in skills}
    # A spread across Singapore-relevant domains, not a toy set.
    assert {"Data & AI", "Cloud", "Cybersecurity", "Finance", "HR", "Logistics"} <= sectors


def test_augment_preserves_baseline_and_divisor():
    base = {"baseline": 100.0, "divisor": 0.0004, "skills": [], "sectors": []}
    augmented = augment_market_with_catalog(base)
    assert augmented["baseline"] == 100.0
    assert augmented["divisor"] == 0.0004
    assert len(augmented["skills"]) == len(CATALOG)


def test_catalogue_skill_is_explainable():
    response = client.get("/api/explain/skill/Machine Learning")
    assert response.status_code == 200
    body = response.json()
    assert body["skill"] == "Machine Learning"
    assert body["formula"]
