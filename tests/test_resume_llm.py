"""LLM-backed resume analysis: grounding guardrails + the AI vs deterministic path.

These tests never hit the network. The fallback path exercises the real (keyless)
code, which must fail closed; the AI path stubs the LLM function so the grounding
and wiring are tested deterministically.
"""

from __future__ import annotations

import skillsmarket.api as api
from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.resume import ground_ai_insight

client = TestClient(app)

RESUME = (
    "Operations analyst skilled in Python and Microsoft Excel. Built weekly dashboards "
    "and reduced reporting time by 30%. Bachelor degree in business analytics."
)


def test_ground_ai_insight_drops_invented_skills_and_quotes():
    raw = {
        "model": "test-model",
        "summary": "Analyst with Python and Excel reporting experience.",
        "strongest_skills": ["Python", "Dragon Taming"],  # 2nd not detected -> dropped
        "high_upside_skills": ["Data Storytelling", "Astrology"],  # 2nd not in vocab -> dropped
        "role_fit": "Data / AI Analyst",
        "next_moves": ["Ship a dashboard", "Learn SQL", "Quantify impact", "Extra move"],  # capped to 3
        "evidence": [
            {"skill": "Python", "quote": "skilled in Python"},  # verbatim -> kept
            {"skill": "Excel", "quote": "ran a marathon in 3 hours"},  # not in text -> dropped
        ],
    }

    insight = ground_ai_insight(
        raw,
        RESUME,
        detected_skills={"Python", "Microsoft Excel"},
        allowed_skills={"Python", "Microsoft Excel", "Data Storytelling", "SQL"},
    )

    assert insight is not None
    assert insight.mode == "ai_assisted"
    assert insight.strongest_skills == ["Python"]
    assert insight.high_upside_skills == ["Data Storytelling"]
    assert len(insight.next_moves) == 3
    assert [quote.quote for quote in insight.evidence] == ["skilled in Python"]


def test_ground_ai_insight_returns_none_when_nothing_survives():
    raw = {
        "strongest_skills": ["Underwater Basket Weaving"],
        "high_upside_skills": ["Astrology"],
        "summary": "",
        "role_fit": "",
        "next_moves": [],
        "evidence": [{"skill": "x", "quote": "not present in the resume at all"}],
    }
    assert ground_ai_insight(raw, RESUME, detected_skills=set(), allowed_skills=set()) is None


def test_analyze_text_fails_closed_to_deterministic_when_llm_unavailable():
    # The autouse fixture makes the LLM call return None (as a missing key would) ->
    # the deterministic readout stands, with an honest analysis_mode.
    response = client.post("/api/resume/analyze-text", json={"text": RESUME})
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_mode"] == "deterministic"
    assert body["ai"] is None
    assert body["skills"]  # deterministic engine still produced a full readout


def test_analyze_text_marks_ai_assisted_when_llm_runs(monkeypatch):
    def fake_llm(text: str, market_skill_names):
        return {
            "model": "stub/model",
            "skills": ["Python", "Microsoft Excel"],
            "summary": "Operations analyst with Python and Excel reporting strength.",
            "strongest_skills": ["Python", "Microsoft Excel"],
            "high_upside_skills": ["Data Storytelling"],
            "role_fit": "Data / AI Analyst",
            "next_moves": ["Ship a Python dashboard", "Add SQL", "Quantify impact"],
            "evidence": [{"skill": "Python", "quote": "skilled in Python"}],
        }

    monkeypatch.setattr(api, "analyze_resume_with_openrouter", fake_llm)

    response = client.post("/api/resume/analyze-text", json={"text": RESUME})
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_mode"] == "ai_assisted"
    assert body["ai"] is not None
    assert body["ai"]["model"] == "stub/model"
    assert "Python" in body["ai"]["strongest_skills"]
    assert body["ai"]["evidence"][0]["quote"] == "skilled in Python"
    # The deterministic, market-priced readout is still present and authoritative.
    assert body["skills"]
    assert any(skill["name"] == "Python" for skill in body["skills"])


def test_analyze_text_stays_deterministic_when_llm_raises(monkeypatch):
    def boom(text: str, market_skill_names):
        raise RuntimeError("network down")

    monkeypatch.setattr(api, "analyze_resume_with_openrouter", boom)

    response = client.post("/api/resume/analyze-text", json={"text": RESUME})
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_mode"] == "deterministic"
    assert body["ai"] is None
