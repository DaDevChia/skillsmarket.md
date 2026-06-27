from __future__ import annotations

from typing import Any

from skillsmarket.engine import ADMIN_SHOCK_SKILLS, AI_SHOCK_SKILLS, BASELINE
from skillsmarket.history import history_stats, seeded_history, source_badges
from skillsmarket.live_evidence import evidence_for_skill
from skillsmarket.skillsfuture import courses_for_skill


def _confidence(skill: dict[str, Any]) -> dict[str, Any]:
    support = int(skill.get("source_row_count") or len(skill.get("source_rows") or []))
    base = min(1.0, support / 12.0)
    seeded = skill.get("provenance") == "seeded"
    score = round(base * (0.6 if seeded else 1.0), 2)
    level = "high" if score >= 0.67 else "medium" if score >= 0.34 else "low"
    limitations: list[str] = []
    if seeded:
        limitations.append("Seeded fixture, not live market data.")
    limitations.append("Supply is an applicant-count proxy, not true labour supply.")
    if skill.get("salary_mid") is None:
        limitations.append("No salary / job-money signal present in this snapshot.")
    if support < 4:
        limitations.append("Thin support — few backing rows.")
    return {"level": level, "score": score, "support": support, "limitations": limitations}


def _shock_effect(name_lower: str) -> dict[str, Any]:
    if name_lower in ADMIN_SHOCK_SKILLS:
        return {"name": "genai", "effect": "down", "multiplier": 0.55,
                "note": "GenAI shock models admin demand dipping (×0.55)."}
    if name_lower in AI_SHOCK_SKILLS:
        return {"name": "genai", "effect": "up", "multiplier": 1.85,
                "note": "GenAI shock models AI / data / automation demand rising (×1.85)."}
    return {"name": "genai", "effect": "neutral", "multiplier": 1.0,
            "note": "Largely unmoved by the modelled GenAI demand shift."}


def build_skill_detail(market: dict[str, Any], skill_id: str) -> dict[str, Any]:
    lookup: dict[str, dict[str, Any]] = {}
    for skill in market.get("skills", []):
        for key in (skill.get("id"), str(skill.get("name", "")).lower(), str(skill.get("symbol", "")).lower()):
            if key:
                lookup.setdefault(str(key), skill)
    skill = lookup.get(skill_id) or lookup.get(skill_id.lower())
    if not skill:
        raise KeyError(skill_id)

    price = float(skill["price"])
    baseline = float(market.get("baseline", BASELINE))
    history = seeded_history(skill["name"], price, days=90)
    stats = history_stats(history, price)
    shock = _shock_effect(skill["name"].lower())

    methodology = {
        "weighted_demand": skill.get("weighted_demand"),
        "supply_proxy": skill.get("supply_proxy"),
        "salary_mid": skill.get("salary_mid"),
        "salary_premium": skill.get("salary_premium"),
        "support": skill.get("source_row_count"),
        "divisor": market.get("divisor"),
        "baseline": baseline,
        "raw_score": skill.get("raw_score"),
        "formula": "(weighted_demand / supply_proxy) / frozen_divisor",
        "provenance": skill.get("provenance"),
        "demand_explainer": "Weighted job-posting support — key skills count 1.5×, soft skills 0.25×.",
        "supply_explainer": "Average applicants per posting that lists the skill — an imperfect supply proxy.",
        "salary_explainer": "Average salary midpoint of postings, used only where present (a job-money proxy).",
        "divisor_explainer": "Frozen so future / shocked snapshots stay comparable to the base market.",
        "baseline_explainer": "100 = the median skill price. Above 100 = scarcer; below = more common.",
    }

    delta = price - baseline
    posture = "scarce / above baseline" if delta >= 0 else "common / below baseline"
    analyst_note = (
        f"{skill['name']} prints {price:.0f} pts ({delta:+.0f} vs {baseline:.0f}) — {posture}. "
        f"{stats['change_30d']:+.1f}% over 30d ({stats['trend']}), 90d range {stats['low']:.0f}–{stats['high']:.0f}. "
        f"{shock['note']}"
    )

    return {
        "skill": skill,
        "history": history,
        "history_label": "Seeded historical proxy — deterministic backtest, not live history.",
        "stats": stats,
        "methodology": methodology,
        "confidence": _confidence(skill),
        "source_badges": source_badges(skill),
        "live_evidence": evidence_for_skill(skill["name"]),
        "courses": courses_for_skill(skill["name"]),
        "shock": shock,
        "analyst_note": analyst_note,
    }
