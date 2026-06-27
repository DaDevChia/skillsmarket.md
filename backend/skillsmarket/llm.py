from __future__ import annotations

import json
from typing import Any, Iterable
import httpx

from skillsmarket.settings import settings

REQUIRED_EXPLANATION_FIELDS = {"skill", "price", "weighted_demand", "supply_proxy", "divisor", "source_rows", "provenance"}


def build_grounded_explanation_prompt(structured_facts: dict[str, Any]) -> str:
    missing = REQUIRED_EXPLANATION_FIELDS - set(structured_facts)
    if missing:
        raise ValueError(f"Missing structured facts: {', '.join(sorted(missing))}")
    return (
        "Explain this SkillsMarket quote in plain English for a Singapore worker. "
        "Do not invent facts, courses, prices, salaries, rows, or sources. "
        "Use only the structured facts below. Keep it under 80 words.\n\n"
        f"Skill: {structured_facts['skill']}\n"
        f"Price: {structured_facts['price']} points\n"
        f"Weighted demand: {structured_facts['weighted_demand']}\n"
        f"Supply proxy: {structured_facts['supply_proxy']}\n"
        f"Frozen divisor: {structured_facts['divisor']}\n"
        f"Source rows: {structured_facts['source_rows']}\n"
        f"Provenance: {structured_facts['provenance']}\n"
    )


def explain_with_openrouter(structured_facts: dict[str, Any]) -> dict[str, Any]:
    prompt = build_grounded_explanation_prompt(structured_facts)
    if not settings.openrouter_api_key:
        return {"mode": "template", "text": structured_facts.get("plain") or prompt}

    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 120,
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=30) as client:
        response = client.post(f"{settings.openrouter_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        body = response.json()
    return {"mode": "openrouter", "model": body.get("model", settings.openrouter_model), "text": body["choices"][0]["message"]["content"].strip()}


def build_resume_extraction_prompt(text: str) -> str:
    """Prompt that constrains the model to resume text only, no invention."""
    return (
        "Extract skills from this resume for a Singapore skills index. "
        "Return strict JSON: {\"name\": string|null, \"current_role\": string|null, \"skills\": string[]}. "
        "Only list skills explicitly evidenced in the text. "
        "Do not invent credentials, education, employers, salaries, or skills.\n\n"
        f"Resume:\n{text[:8000]}"
    )


def extract_resume_skills_with_openrouter(text: str) -> list[str] | None:
    """Best-effort LLM skill extraction. Returns None on any failure.

    Callers must treat the result as untrusted and intersect it with the known
    market vocabulary (see ``resume.merge_llm_skills_with_deterministic``) so the
    model can never widen the skill set with invented entries. Fails closed: no
    key, no network, malformed JSON -> None, and the deterministic parser stands.
    """
    if not settings.openrouter_api_key or not text.strip():
        return None
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": build_resume_extraction_prompt(text)}],
        "temperature": 0.0,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        skills = parsed.get("skills")
        if not isinstance(skills, Iterable):
            return None
        return [str(skill) for skill in skills if isinstance(skill, str)]
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None


def build_resume_analysis_prompt(text: str, market_skill_names: list[str]) -> str:
    """Prompt for the richer 'AI analyst' readout. Hard-constrained to the supplied
    resume text — the model may narrate, but may not invent resume facts, and every
    quote must be copied verbatim (the caller re-verifies this)."""
    vocabulary = ", ".join(sorted(market_skill_names)[:120])
    return (
        "You are a senior Singapore career analyst reviewing a resume against a live skills market. "
        "Use ONLY the resume text below. Do NOT invent employers, job titles, dates, numbers, "
        "credentials, or skills the candidate has not stated. Every 'quote' you return MUST be copied "
        "verbatim (character-for-character) from the resume text.\n"
        "Return STRICT JSON only, with exactly this shape:\n"
        '{"skills": string[], '
        '"summary": string (<=55 words, factual, grounded in the text), '
        '"strongest_skills": string[] (<=5 skills the candidate clearly evidences), '
        '"high_upside_skills": string[] (<=5 adjacent, in-demand skills worth learning next), '
        '"role_fit": string (<=30 words), '
        '"next_moves": string[] (exactly 3 concrete learning / positioning moves), '
        '"evidence": [{"skill": string, "quote": string}] (<=5; quote copied verbatim from the resume)}\n\n'
        "Prefer skill names from this market vocabulary where they fit:\n"
        f"{vocabulary}\n\n"
        f"Resume:\n{text[:8000]}"
    )


def analyze_resume_with_openrouter(text: str, market_skill_names: list[str]) -> dict[str, Any] | None:
    """Best-effort richer LLM resume analysis. Returns None on any failure.

    Fails closed: no key, no text, network error, or malformed JSON all yield None
    and the deterministic analysis stands. The caller MUST re-ground every field
    (intersect skills with the market vocabulary, verify quotes are verbatim) so the
    model can never widen the skill set or invent resume facts.
    """
    if not settings.openrouter_api_key or not text.strip():
        return None
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": build_resume_analysis_prompt(text, market_skill_names)}],
        "temperature": 0.2,
        "max_tokens": 700,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=45) as client:
            response = client.post(
                f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None
    if not isinstance(parsed, dict):
        return None
    parsed["model"] = settings.openrouter_model
    return parsed


def research_skill_with_openrouter(name: str) -> dict[str, Any] | None:
    """Live LLM research for a skill not on the market. Returns a structured,
    clearly-labelled *estimate* (never presented as real market data). Fails
    closed to None on no key / network / parse error.
    """
    if not settings.openrouter_api_key or not name.strip():
        return None
    prompt = (
        "You are a Singapore labour-market analyst. For the skill below, return STRICT JSON only: "
        '{"sector": string, "scarcity": "scarce"|"mid"|"common", "est_index": number 40-240 '
        "(100 = median, higher = scarcer/higher-paid), "
        '"est_salary_min": number, "est_salary_max": number (SGD monthly), '
        '"summary": string <=45 words, "role_direction": string, "course_query": string}. '
        "Use general knowledge of the Singapore market. Do NOT invent specific employers, live counts, or sources.\n\n"
        f"Skill: {name.strip()[:120]}"
    )
    payload = {
        "model": settings.openrouter_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 300,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"}
    try:
        with httpx.Client(timeout=40) as client:
            response = client.post(
                f"{settings.openrouter_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
    except (httpx.HTTPError, KeyError, ValueError, TypeError):
        return None
    if not isinstance(parsed, dict) or "est_index" not in parsed:
        return None
    return {
        "name": name.strip(),
        "provenance": "ai_researched",
        "disclaimer": "AI-researched estimate from a language model — not real market data.",
        "model": settings.openrouter_model,
        "sector": str(parsed.get("sector") or "Unclassified"),
        "scarcity": str(parsed.get("scarcity") or "mid"),
        "est_index": float(parsed.get("est_index") or 100),
        "est_salary_min": parsed.get("est_salary_min"),
        "est_salary_max": parsed.get("est_salary_max"),
        "summary": str(parsed.get("summary") or ""),
        "role_direction": str(parsed.get("role_direction") or ""),
        "course_query": str(parsed.get("course_query") or name.strip()),
    }
