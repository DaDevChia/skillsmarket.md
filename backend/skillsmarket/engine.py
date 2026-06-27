from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any

KEY_SKILL_WEIGHT = 1.5
PERIPHERAL_SKILL_WEIGHT = 1.0
SOFT_SKILL_MULTIPLIER = 0.25
BASELINE = 100.0

SOFT_SKILLS = {
    "communication",
    "team player",
    "teamwork",
    "leadership",
    "interpersonal skills",
    "problem solving",
    "customer service",
}

ADMIN_SHOCK_SKILLS = {"administration", "microsoft excel", "scheduling", "customer service", "communication", "team player"}
AI_SHOCK_SKILLS = {"ai-assisted operations", "workflow automation", "data analysis", "data storytelling", "python"}


def _canonical(name: str) -> str:
    return " ".join(str(name).strip().split())


def _skill_id(name: str) -> str:
    return _canonical(name).lower().replace(" ", "-").replace("/", "-")


def _is_soft_skill(name: str) -> bool:
    return _canonical(name).lower() in SOFT_SKILLS


def compute_market(
    postings: list[dict[str, Any]],
    min_support: int = 2,
    frozen_divisor: float | None = None,
    demand_multipliers: dict[str, float] | None = None,
    provenance: str = "seeded",
) -> dict[str, Any]:
    """Compute skill prices and demand-weighted sector indices.

    Demand is weighted posting support. Key skills count more than peripheral tags.
    Supply is the average applicant competition for postings containing the skill.
    A frozen divisor keeps future/shocked snapshots comparable to the base market.
    """

    demand_multipliers = {k.lower(): v for k, v in (demand_multipliers or {}).items()}
    skill_stats: dict[str, dict[str, Any]] = {}

    for posting in postings:
        applications = float(posting.get("applications") or 1)
        applications = max(applications, 1.0)
        sector = posting.get("sector") or "Unclassified"
        salary_min = posting.get("salary_min")
        salary_max = posting.get("salary_max")

        for skill in posting.get("skills", []):
            name = _canonical(skill.get("name", ""))
            if not name:
                continue

            base_weight = KEY_SKILL_WEIGHT if skill.get("is_key") else PERIPHERAL_SKILL_WEIGHT
            soft_multiplier = SOFT_SKILL_MULTIPLIER if _is_soft_skill(name) else 1.0
            shock_multiplier = demand_multipliers.get(name.lower(), 1.0)
            weight = base_weight * soft_multiplier * shock_multiplier

            stats = skill_stats.setdefault(
                name,
                {
                    "id": skill.get("id") or _skill_id(name),
                    "name": name,
                    "support": 0,
                    "weighted_demand": 0.0,
                    "applications": [],
                    "sector_weights": defaultdict(float),
                    "source_rows": [],
                    "salary_values": [],
                    "is_soft_skill": _is_soft_skill(name),
                },
            )
            stats["support"] += 1
            stats["weighted_demand"] += weight
            stats["applications"].append(applications)
            stats["sector_weights"][sector] += weight
            stats["source_rows"].append(posting.get("id"))
            if salary_min and salary_max:
                stats["salary_values"].append((float(salary_min) + float(salary_max)) / 2.0)

    priced_skills = []
    for stats in skill_stats.values():
        if stats["support"] < min_support:
            continue

        supply = sum(stats["applications"]) / len(stats["applications"])
        raw_score = stats["weighted_demand"] / max(supply, 1.0)
        salary_mid = sum(stats["salary_values"]) / len(stats["salary_values"]) if stats["salary_values"] else None
        priced_skills.append(
            {
                "id": stats["id"],
                "symbol": _symbol_for(stats["name"]),
                "name": stats["name"],
                "support": stats["support"],
                "demand": round(stats["weighted_demand"], 4),
                "weighted_demand": round(stats["weighted_demand"], 4),
                "supply": round(supply, 4),
                "supply_proxy": round(supply, 4),
                "raw_score": raw_score,
                "source_rows": [row for row in stats["source_rows"] if row],
                "source_row_count": len([row for row in stats["source_rows"] if row]),
                "sector_weights": dict(stats["sector_weights"]),
                "salary_mid": round(salary_mid, 2) if salary_mid else None,
                "salary_premium": None,
                "is_soft_skill": stats["is_soft_skill"],
                "provenance": provenance,
                "unit": "points",
            }
        )

    if not priced_skills:
        return {"baseline": BASELINE, "divisor": frozen_divisor or 1.0, "skills": [], "sectors": []}

    raw_median = median(skill["raw_score"] for skill in priced_skills)
    divisor = frozen_divisor if frozen_divisor is not None else (raw_median / BASELINE if raw_median else 1.0)
    median_salary = median([skill["salary_mid"] for skill in priced_skills if skill["salary_mid"]]) if any(skill["salary_mid"] for skill in priced_skills) else None

    for skill in priced_skills:
        skill["price"] = round(skill["raw_score"] / divisor, 2) if divisor else 0.0
        skill["change"] = _seeded_change(skill["name"], skill["price"])
        if median_salary and skill["salary_mid"]:
            skill["salary_premium"] = round(skill["salary_mid"] / median_salary, 2)

    sector_totals: dict[str, dict[str, float]] = defaultdict(lambda: {"weighted_sum": 0.0, "demand": 0.0})
    for skill in priced_skills:
        for sector, weight in skill["sector_weights"].items():
            sector_totals[sector]["weighted_sum"] += skill["price"] * weight
            sector_totals[sector]["demand"] += weight

    sectors = []
    for name, stats in sector_totals.items():
        demand = stats["demand"] or 1.0
        sectors.append(
            {
                "name": name,
                "symbol": _symbol_for(name),
                "index": round(stats["weighted_sum"] / demand, 2),
                "demand": round(stats["demand"], 4),
                "change": _seeded_change(name, stats["weighted_sum"] / demand),
                "unit": "points",
                "provenance": provenance,
            }
        )

    clean_skills = []
    for skill in priced_skills:
        clean_skill = dict(skill)
        sector_weights = clean_skill.pop("sector_weights", {})
        sorted_sectors = sorted(sector_weights.items(), key=lambda item: item[1], reverse=True)
        clean_skill["sector"] = sorted_sectors[0][0] if sorted_sectors else "Unclassified"
        clean_skill["sectors"] = [{"name": name, "weight": round(weight, 4)} for name, weight in sorted_sectors]
        clean_skill["raw_score"] = round(clean_skill["raw_score"], 6)
        clean_skills.append(clean_skill)

    return {
        "baseline": BASELINE,
        "divisor": round(divisor, 8),
        "skills": sorted(clean_skills, key=lambda item: item["price"], reverse=True),
        "sectors": sorted(sectors, key=lambda item: item["index"], reverse=True),
    }


def _symbol_for(name: str) -> str:
    words = [w for w in _canonical(name).replace("-", " ").split() if w]
    if not words:
        return "SKL"
    if len(words) == 1:
        return words[0][:4].upper()
    return "".join(word[0] for word in words[:4]).upper()


def _seeded_change(name: str, price: float) -> float:
    checksum = sum(ord(c) for c in name)
    direction = 1 if price >= BASELINE else -1
    return round(direction * (1.5 + (checksum % 70) / 10), 1)


def skill_lookup(market: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for skill in market.get("skills", []):
        for key in (skill.get("name"), skill.get("id"), skill.get("symbol")):
            if key:
                lookup[str(key)] = skill
                lookup[str(key).lower()] = skill
    return lookup


def compute_career_index(market: dict[str, Any], holdings: list[str]) -> dict[str, Any]:
    lookup = skill_lookup(market)
    components = []
    total = 0.0
    weight_total = 0.0
    for holding in holdings:
        skill = lookup.get(holding)
        price = float(skill["price"]) if skill else 75.0
        weight = float(skill.get("demand", 1.0)) if skill else 1.0
        total += price * weight
        weight_total += weight
        components.append(
            {
                "skill": holding,
                "price": round(price, 2),
                "weight": round(weight, 4),
                "status": "priced" if skill else "missing_default",
            }
        )
    index = total / weight_total if weight_total else BASELINE
    return {"index": round(index, 1), "baseline": BASELINE, "components": components, "unit": "points"}


def recommended_trades(persona: dict[str, Any], market: dict[str, Any], courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for skill_name in persona.get("target_skills", []):
        if skill_name in persona.get("holdings", []):
            continue
        try:
            results.append(simulate_trade(persona, market, courses, target_skill=skill_name))
        except ValueError:
            continue
    return sorted(results, key=lambda row: row["delta"], reverse=True)


def simulate_trade(persona: dict[str, Any], market: dict[str, Any], courses: list[dict[str, Any]], target_skill: str) -> dict[str, Any]:
    lookup = skill_lookup(market)
    if target_skill not in lookup:
        raise ValueError(f"Unknown target skill: {target_skill}")
    course = next((course for course in courses if course["mapped_skill"] == target_skill), None)
    if not course:
        raise ValueError(f"No course mapped to skill: {target_skill}")

    before = compute_career_index(market, persona.get("holdings", []))
    after_holdings = list(dict.fromkeys([*persona.get("holdings", []), target_skill]))
    after = compute_career_index(market, after_holdings)
    delta = round(after["index"] - before["index"], 1)
    skill = lookup[target_skill]
    return {
        "persona_id": persona["id"],
        "skill": target_skill,
        "before_index": before["index"],
        "after_index": after["index"],
        "delta": delta,
        "unit": "points",
        "course": course,
        "provenance": course["provenance"],
        "explanation": f"Acquire {target_skill}: price {skill['price']} points from {skill['source_row_count']} source rows, raising the Career Index by {delta} points.",
    }


def explain_skill(market: dict[str, Any], skill_name: str) -> dict[str, Any]:
    lookup = skill_lookup(market)
    skill = lookup.get(skill_name) or lookup.get(skill_name.lower())
    if not skill:
        raise KeyError(skill_name)
    return {
        "skill": skill["name"],
        "symbol": skill["symbol"],
        "price": skill["price"],
        "unit": "points",
        "weighted_demand": skill["weighted_demand"],
        "supply_proxy": skill["supply_proxy"],
        "divisor": market["divisor"],
        "source_rows": skill["source_row_count"],
        "source_row_ids": skill["source_rows"],
        "formula": "(weighted_demand / supply_proxy) / frozen_divisor",
        "provenance": skill["provenance"],
        "salary_premium": skill.get("salary_premium"),
        "plain": f"{skill['name']} is quoted at {skill['price']} points because weighted demand {skill['weighted_demand']} is divided by competition proxy {skill['supply_proxy']} and normalised by the frozen divisor {market['divisor']}.",
    }


def apply_market_shock(postings: list[dict[str, Any]], base_market: dict[str, Any], shock_name: str = "genai") -> dict[str, Any]:
    if shock_name != "genai":
        raise ValueError(f"Unknown shock: {shock_name}")
    multipliers: dict[str, float] = {}
    for skill in base_market.get("skills", []):
        lowered = skill["name"].lower()
        if lowered in ADMIN_SHOCK_SKILLS:
            multipliers[skill["name"]] = 0.55
        elif lowered in AI_SHOCK_SKILLS:
            multipliers[skill["name"]] = 1.85
    shocked = compute_market(postings, min_support=1, frozen_divisor=base_market["divisor"], demand_multipliers=multipliers)
    base_prices = skill_lookup(base_market)
    changed = []
    for skill in shocked["skills"]:
        old = base_prices.get(skill["name"], {}).get("price")
        if old is not None and abs(skill["price"] - old) >= 0.01:
            changed.append({"skill": skill["name"], "before": old, "after": skill["price"], "delta": round(skill["price"] - old, 2)})
    shocked["shock"] = {
        "name": "genai",
        "label": "GenAI breakthrough",
        "message": "Automation is modelled as a demand shift, not a black-box doom score.",
        "preserves_divisor": True,
    }
    shocked["changed_skills"] = sorted(changed, key=lambda row: abs(row["delta"]), reverse=True)
    return shocked
