from skillsmarket.engine import (
    apply_market_shock,
    compute_career_index,
    compute_market,
    explain_skill,
    simulate_trade,
)
from skillsmarket.fixtures import COURSES, PERSONAS, demo_postings
from skillsmarket.ingest import normalize_mycareersfuture_job


def test_normalize_mycareersfuture_job_extracts_required_fields():
    raw = {
        "uuid": "abc",
        "title": "Data Analyst",
        "metadata": {"totalNumberJobApplication": 7, "newPostingDate": "2026-06-01"},
        "salary": {"minimum": 3000, "maximum": 5000},
        "categories": [{"name": "Information Technology"}],
        "positionLevels": [{"name": "Professional"}],
        "ssocCode": "2521",
        "skills": [
            {"skill": "Python", "uuid": "py", "isKeySkill": True},
            {"skill": "Team Player", "uuid": "team", "isKeySkill": False},
        ],
    }

    posting = normalize_mycareersfuture_job(raw)

    assert posting["id"] == "abc"
    assert posting["applications"] == 7
    assert posting["sector"] == "Information Technology"
    assert posting["salary_min"] == 3000
    assert posting["salary_max"] == 5000
    assert posting["skills"] == [
        {"id": "py", "name": "Python", "is_key": True},
        {"id": "team", "name": "Team Player", "is_key": False},
    ]


def test_compute_market_filters_low_support_and_downweights_soft_skills():
    postings = [
        {"id": "1", "applications": 10, "sector": "Tech", "skills": [{"name": "Python", "is_key": True}, {"name": "Team Player", "is_key": True}]},
        {"id": "2", "applications": 12, "sector": "Tech", "skills": [{"name": "Python", "is_key": True}, {"name": "Team Player", "is_key": True}]},
        {"id": "3", "applications": 4, "sector": "Tech", "skills": [{"name": "Rare One-Off", "is_key": True}]},
    ]

    market = compute_market(postings, min_support=2)
    prices = {skill["name"]: skill["price"] for skill in market["skills"]}

    assert "Rare One-Off" not in prices
    assert prices["Python"] > prices["Team Player"]
    assert next(skill for skill in market["skills"] if skill["name"] == "Team Player")["provenance"] == "seeded"


def test_career_index_and_simulate_trade_raise_persona_index():
    market = compute_market(demo_postings(), min_support=1)
    persona = PERSONAS["mdm-lim"]

    before = compute_career_index(market, persona["holdings"])
    trade = simulate_trade(persona, market, COURSES, target_skill="Data Storytelling")

    assert before["index"] < 100
    assert trade["before_index"] == before["index"]
    assert trade["after_index"] > trade["before_index"]
    assert trade["delta"] > 0
    assert trade["course"]["mapped_skill"] == "Data Storytelling"
    assert "provenance" in trade["course"]


def test_genai_shock_keeps_divisor_and_reprices_expected_skills():
    base = compute_market(demo_postings(), min_support=1)
    shocked = apply_market_shock(demo_postings(), base_market=base, shock_name="genai")

    base_prices = {skill["name"]: skill["price"] for skill in base["skills"]}
    shock_prices = {skill["name"]: skill["price"] for skill in shocked["skills"]}

    assert shocked["divisor"] == base["divisor"]
    assert shock_prices["Administration"] < base_prices["Administration"]
    assert shock_prices["AI-Assisted Operations"] > base_prices["AI-Assisted Operations"]
    assert shocked["shock"]["name"] == "genai"


def test_explain_skill_returns_formula_and_source_rows():
    market = compute_market(demo_postings(), min_support=1)

    explanation = explain_skill(market, "Microsoft Excel")

    assert explanation["skill"] == "Microsoft Excel"
    assert explanation["formula"] == "(weighted_demand / supply_proxy) / frozen_divisor"
    assert explanation["source_rows"] >= 1
    assert explanation["unit"] == "points"
    assert explanation["provenance"] in {"real", "real_proxy", "curated_demo", "seeded"}
