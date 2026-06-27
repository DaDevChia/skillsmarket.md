from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from skillsmarket.courses import COURSE_NOTE, course_search_url
from skillsmarket.skill_catalog import CATALOG


class ResumeExample(BaseModel):
    id: str
    label: str
    role: str
    text: str


class ParsedResume(BaseModel):
    name: str | None = None
    current_role: str | None = None
    skills: list[str] = Field(default_factory=list)
    evidence: dict[str, list[str]] = Field(default_factory=dict)


class IndexedResumeSkill(BaseModel):
    name: str
    matched_skill: str | None
    price: float | None
    baseline_delta: float | None
    sector: str | None
    status: str
    evidence: list[str] = Field(default_factory=list)


class ResumeHighlight(BaseModel):
    start: int
    end: int
    text: str
    category: str  # skill | weak | role | education | achievement
    label: str
    detail: str
    confidence: float
    skill: str | None = None
    affects: str | None = None


class ResumeAction(BaseModel):
    type: str
    title: str
    skill: str | None = None
    why: str
    how_to_prove: str
    role_direction: str
    market_price: float | None = None
    course_query: str | None = None
    course_url: str | None = None
    course_note: str = COURSE_NOTE


class ResumeEvidenceQuote(BaseModel):
    skill: str
    quote: str


class ResumeAiInsight(BaseModel):
    """The grounded 'AI analyst' readout. Every field is re-verified against the
    supplied resume text before it reaches here — invented skills and non-verbatim
    quotes are dropped — so it is AI-narrated but evidence-bounded."""

    mode: str = "ai_assisted"
    model: str | None = None
    summary: str = ""
    strongest_skills: list[str] = Field(default_factory=list)
    high_upside_skills: list[str] = Field(default_factory=list)
    role_fit: str = ""
    next_moves: list[str] = Field(default_factory=list)
    evidence: list[ResumeEvidenceQuote] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    source: str
    parsed: ParsedResume
    document_text: str
    personal_index: float
    baseline: float
    skills: list[IndexedResumeSkill]
    strengths: list[IndexedResumeSkill]
    gaps: list[IndexedResumeSkill]
    highlights: list[ResumeHighlight]
    actions: list[ResumeAction]
    methodology_summary: str
    # 'ai_assisted' when the LLM analyst ran and grounded cleanly; else 'deterministic'.
    analysis_mode: str = "deterministic"
    ai: ResumeAiInsight | None = None


# ---- skill vocabulary -------------------------------------------------------

# Curated abbreviations/variants on top of the literal skill names.
_VARIANTS: dict[str, str] = {
    "excel": "Microsoft Excel",
    "spreadsheet": "Microsoft Excel",
    "spreadsheets": "Microsoft Excel",
    "data analytics": "Data Analysis",
    "statistics": "Data Analysis",
    "forecasting": "Data Analysis",
    "data visualisation": "Data Storytelling",
    "data visualization": "Data Storytelling",
    "dashboard": "Data Storytelling",
    "dashboards": "Data Storytelling",
    "dashboarding": "Data Storytelling",
    "automation": "Workflow Automation",
    "administrative": "Administration",
    "procurement coordination": "Administration",
    "presenting": "Communication",
    "ai operations": "AI-Assisted Operations",
    "ai-assisted": "AI-Assisted Operations",
    "mlops": "MLOps Engineering",
    "sustainability": "Sustainability Reporting",
    "ml": "Machine Learning",
    "nlp": "Natural Language Processing",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "llm": "Generative AI",
    "llms": "Generative AI",
    "aws": "Amazon Web Services",
    "azure": "Microsoft Azure",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "k8s": "Kubernetes",
    "ci/cd": "CI/CD Pipelines",
    "sre": "Site Reliability Engineering",
    "powerbi": "Power BI",
    "reactjs": "React",
    "react.js": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "js": "JavaScript",
    "go": "Golang",
    "scrum": "Agile & Scrum",
    "agile": "Agile & Scrum",
    "kanban": "Agile & Scrum",
    "seo": "Search Engine Optimisation",
    "crm": "CRM Management",
    "esg": "ESG Reporting",
    "six sigma": "Lean Six Sigma",
    "lean": "Lean Six Sigma",
    "soc": "Security Operations (SOC)",
    "pentest": "Penetration Testing",
    "pen testing": "Penetration Testing",
    "iam": "Identity & Access Management",
    "etl": "ETL Pipelines",
    "spark": "Big Data (Spark)",
    "wsh": "Workplace Safety (WSH)",
    "payroll": "Payroll Administration",
    "financial modeling": "Financial Modelling",
}


def _build_alias_map() -> dict[str, str]:
    aliases: dict[str, str] = {
        # core engine-priced skills
        "microsoft excel": "Microsoft Excel",
        "python": "Python",
        "data analysis": "Data Analysis",
        "data storytelling": "Data Storytelling",
        "workflow automation": "Workflow Automation",
        "customer service": "Customer Service",
        "administration": "Administration",
        "scheduling": "Scheduling",
        "communication": "Communication",
        "ai-assisted operations": "AI-Assisted Operations",
        "sustainability reporting": "Sustainability Reporting",
    }
    for name, _sector, _tier in CATALOG:
        aliases.setdefault(name.lower(), name)
    aliases.update(_VARIANTS)
    return aliases


SKILL_ALIASES: dict[str, str] = _build_alias_map()


SECTOR_ROLE: dict[str, str] = {
    "Data & AI": "Data / AI Analyst",
    "Cloud": "Cloud / DevOps Engineer",
    "Cybersecurity": "Security Analyst",
    "Software": "Software Engineer",
    "Finance": "Finance Analyst",
    "HR": "People / HR Analytics",
    "Logistics": "Supply Chain Analyst",
    "Operations": "Operations Analyst",
    "Sales & Marketing": "Growth / Marketing Analyst",
    "Project Management": "Project Manager",
    "Sustainability": "Sustainability Analyst",
    "Manufacturing": "Process / Manufacturing Engineer",
    "Healthcare Admin": "Healthcare Operations Executive",
    "Education": "Learning & Development Specialist",
    "Communication": "Communications Specialist",
    "Admin": "Operations Coordinator",
    "Tech": "Data-enabled Operations",
    "Green": "Sustainability Analyst",
}

ROLE_TERMS = [
    "executive", "analyst", "engineer", "coordinator", "manager", "associate",
    "specialist", "administrator", "officer", "assistant", "consultant", "lead",
    "director", "technician", "supervisor", "accountant", "developer", "designer",
    "architect", "scientist", "graduate", "intern", "secretary", "clerk",
]

EDUCATION_TERMS = [
    "degree", "diploma", "bachelor", "bachelor's", "master", "master's", "phd",
    "doctorate", "certification", "certified", "certificate", "polytechnic",
    "university", "nitec", "ite", "gce", "cissp", "pmp", "cfa", "scrum master",
    "coursework", "capstone",
]

ACHIEVEMENT_PATTERNS = [
    re.compile(r"\d{1,3}(?:\.\d+)?\s?%"),
    re.compile(r"S?\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmM]?\b"),
    re.compile(r"\b\d+\+?\s+years?\b", re.IGNORECASE),
    re.compile(r"\b\d{1,3}(?:,\d{3})+\b"),
]

METHODOLOGY_SUMMARY = (
    "100 = Singapore median skill price. Above 100 is scarce; below 100 is common. "
    "Price = weighted demand / supply proxy, normalised by a frozen divisor."
)


@lru_cache(maxsize=2048)
def _alias_pattern(alias: str) -> re.Pattern[str]:
    # Token boundaries that respect punctuation in names like node.js or ci/cd.
    return re.compile(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])")


def _iter_alias_spans(lowered: str, alias: str):
    for match in _alias_pattern(alias).finditer(lowered):
        yield match.start(), match.end()


def _evidence_snippet(text: str, start: int, end: int) -> str:
    lo = max(0, start - 32)
    hi = min(len(text), end + 32)
    snippet = re.sub(r"\s+", " ", text[lo:hi].strip())
    return f"{'…' if lo > 0 else ''}{snippet}{'…' if hi < len(text) else ''}"


def parse_resume_text(text: str) -> ParsedResume:
    """Deterministically extract known skills with token-boundary matching."""
    lowered = text.lower()
    skills: list[str] = []
    evidence: dict[str, list[str]] = {}
    for alias in sorted(SKILL_ALIASES, key=len, reverse=True):
        canonical = SKILL_ALIASES[alias]
        if canonical in skills:
            continue
        first = next(_iter_alias_spans(lowered, alias), None)
        if first is not None:
            skills.append(canonical)
            evidence[canonical] = [_evidence_snippet(text, first[0], first[1])]
    skills.sort()
    return ParsedResume(skills=skills, evidence=evidence, current_role=_detect_role(text))


def _detect_role(text: str) -> str | None:
    lowered = text.lower()
    best: tuple[int, str] | None = None
    for term in ROLE_TERMS:
        match = re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lowered)
        if match and (best is None or match.start() < best[0]):
            best = (match.start(), term)
    return best[1].title() if best else None


def _market_lookup(market: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(skill["name"]).lower(): skill for skill in market.get("skills", [])}


# ---- highlights -------------------------------------------------------------

def build_highlights(
    text: str,
    indexed: list[IndexedResumeSkill],
    baseline: float,
    primary_action_skill: str | None,
) -> list[ResumeHighlight]:
    lowered = text.lower()
    by_canonical = {skill.name: skill for skill in indexed}
    # (start, end, priority, category, label, detail, confidence, skill, affects)
    candidates: list[tuple[int, int, int, str, str, str, float, str | None, str | None]] = []

    for alias in sorted(SKILL_ALIASES, key=len, reverse=True):
        canonical = SKILL_ALIASES[alias]
        skill = by_canonical.get(canonical)
        if skill is None:
            continue
        exact = alias == canonical.lower()
        if skill.price is None:
            category, detail = "skill", f"Recognised skill '{canonical}', not yet on the SkillsMarket index."
        elif skill.price < baseline:
            category = "weak"
            detail = (
                f"'{canonical}' prices at {skill.price:.0f} pts, "
                f"{abs(skill.baseline_delta or 0):.0f} below the {baseline:.0f} baseline — common, not differentiating."
            )
        else:
            category = "skill"
            detail = (
                f"'{canonical}' prices at {skill.price:.0f} pts, "
                f"{skill.baseline_delta or 0:+.0f} vs baseline — a scarce differentiator."
            )
        affects = primary_action_skill if (skill.price is not None and skill.price < baseline) else None
        for start, end in _iter_alias_spans(lowered, alias):
            candidates.append((start, end, 1, category, canonical, detail, 0.9 if exact else 0.72, canonical, affects))

    for term in ROLE_TERMS:
        for match in re.finditer(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lowered):
            span = text[match.start():match.end()]
            candidates.append((match.start(), match.end(), 3, "role", "Role / title",
                               f"'{span}' reads as a job title — it anchors your suggested role direction.", 0.65, None, None))

    for term in EDUCATION_TERMS:
        for match in re.finditer(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", lowered):
            span = text[match.start():match.end()]
            candidates.append((match.start(), match.end(), 4, "education", "Education / credential",
                               f"'{span}' is an education or certification signal — adds credibility, not priced directly.", 0.7, None, None))

    for pattern in ACHIEVEMENT_PATTERNS:
        for match in pattern.finditer(text):
            span = match.group(0).strip()
            if not span:
                continue
            candidates.append((match.start(), match.start() + len(match.group(0)), 2, "achievement", "Measurable achievement",
                               f"'{span}' is a quantified result — use it to prove impact on your resume.", 0.75, None, None))

    candidates.sort(key=lambda c: (c[0], c[2], -(c[1] - c[0])))
    chosen: list[ResumeHighlight] = []
    occupied: list[tuple[int, int]] = []
    for start, end, _prio, category, label, detail, confidence, skill, affects in candidates:
        if any(not (end <= os or start >= oe) for os, oe in occupied):
            continue
        occupied.append((start, end))
        chosen.append(ResumeHighlight(start=start, end=end, text=text[start:end], category=category,
                                      label=label, detail=detail, confidence=confidence, skill=skill, affects=affects))
    chosen.sort(key=lambda h: h.start)
    return chosen


# ---- actions ----------------------------------------------------------------

def _build_actions(
    text: str,
    parsed: ParsedResume,
    indexed: list[IndexedResumeSkill],
    market: dict[str, Any],
    baseline: float,
) -> list[ResumeAction]:
    matched = [skill for skill in indexed if skill.price is not None]
    if not matched:
        return [
            ResumeAction(
                type="expand",
                title="Add more detail or pick an example",
                skill=None,
                why="No market-indexed skills were detected in this text yet.",
                how_to_prove="Paste a fuller resume, upload a PDF/DOCX, or choose an example profile.",
                role_direction="—",
            )
        ]

    have = {skill.matched_skill for skill in matched}
    strengths = [skill for skill in matched if skill.price is not None and skill.price >= baseline]
    gaps = [skill for skill in matched if skill.price is not None and skill.price < baseline]
    candidates = sorted(
        [skill for skill in market.get("skills", []) if skill["name"] not in have and float(skill["price"]) >= baseline],
        key=lambda skill: (-float(skill["price"]), skill["name"]),
    )

    actions: list[ResumeAction] = []
    anchor = gaps[0].name if gaps else (strengths[-1].name if strengths else "your current skills")
    for target in candidates[:3]:
        name = str(target["name"])
        price = float(target["price"])
        sector = str(target.get("sector") or "Tech")
        actions.append(
            ResumeAction(
                type="learn",
                title=f"Learn {name}",
                skill=name,
                why=(
                    f"{name} prices at {price:.0f} pts ({price - baseline:+.0f} vs the {baseline:.0f} baseline). "
                    f"Against your evidence ({anchor}), it is the fastest index lift in {sector}."
                ),
                how_to_prove=f"Ship one small {name} project and quantify the outcome; list it under a Projects section with a metric.",
                role_direction=SECTOR_ROLE.get(sector, "Specialist"),
                market_price=round(price, 1),
                course_query=name,
                course_url=course_search_url(name),
            )
        )

    if strengths:
        top = max(strengths, key=lambda skill: skill.price or 0.0)
        actions.append(
            ResumeAction(
                type="prove",
                title=f"Lead with {top.name}",
                skill=top.name,
                why=f"{top.name} is your scarcest asset at {top.price:.0f} pts ({(top.baseline_delta or 0):+.0f} vs baseline). Put it first.",
                how_to_prove=f"Move {top.name} to the top of your resume and pair it with a measurable result.",
                role_direction=SECTOR_ROLE.get(top.sector or "Tech", "Specialist"),
                market_price=top.price,
                course_query=top.name,
                course_url=course_search_url(top.name),
            )
        )

    target_sector = str((candidates[0].get("sector") if candidates else (strengths[0].sector if strengths else "Tech")) or "Tech")
    role = SECTOR_ROLE.get(target_sector, "Specialist")
    detected = parsed.current_role
    actions.append(
        ResumeAction(
            type="direction",
            title=f"Aim for {role}",
            skill=None,
            why=f"Your evidence{f' as a {detected}' if detected else ''} plus the gaps above point toward {role}.",
            how_to_prove=f"Reframe your summary around {role}; mirror the skills priced above baseline.",
            role_direction=role,
            course_query=role,
            course_url=course_search_url(role),
        )
    )
    return actions[:5]


def analyze_resume_text(
    text: str,
    market: dict[str, Any],
    source: str = "paste",
    parsed: ParsedResume | None = None,
) -> ResumeAnalysis:
    """Index a resume against the current SkillsMarket snapshot, with highlights."""
    parsed = parsed or parse_resume_text(text)
    lookup = _market_lookup(market)
    baseline = float(market.get("baseline", 100.0))

    indexed: list[IndexedResumeSkill] = []
    priced: list[float] = []
    for name in parsed.skills:
        skill = lookup.get(name.lower())
        evidence = parsed.evidence.get(name, [])
        if skill:
            price = float(skill["price"])
            priced.append(price)
            indexed.append(
                IndexedResumeSkill(
                    name=name,
                    matched_skill=skill["name"],
                    price=round(price, 2),
                    baseline_delta=round(price - baseline, 2),
                    sector=skill.get("sector"),
                    status="strength" if price >= baseline else "gap",
                    evidence=evidence,
                )
            )
        else:
            indexed.append(
                IndexedResumeSkill(
                    name=name,
                    matched_skill=None,
                    price=None,
                    baseline_delta=None,
                    sector=None,
                    status="unmatched",
                    evidence=evidence,
                )
            )

    indexed.sort(key=lambda skill: (skill.price is not None, skill.price or 0.0), reverse=True)

    personal_index = round(sum(priced) / len(priced), 1) if priced else 0.0
    strengths = [skill for skill in indexed if skill.price is not None and skill.price >= baseline]
    gaps = [skill for skill in indexed if skill.price is not None and skill.price < baseline]
    actions = _build_actions(text, parsed, indexed, market, baseline)
    primary = next((action.skill for action in actions if action.type == "learn"), None)
    highlights = build_highlights(text, indexed, baseline, primary)

    return ResumeAnalysis(
        source=source,
        parsed=parsed,
        document_text=text,
        personal_index=personal_index,
        baseline=baseline,
        skills=indexed,
        strengths=strengths,
        gaps=gaps,
        highlights=highlights,
        actions=actions,
        methodology_summary=METHODOLOGY_SUMMARY,
    )


def enrich_parsed_with_llm(
    parsed: ParsedResume,
    text: str,
    llm_skill_names: list[str],
    allowed_skills: set[str],
) -> ParsedResume:
    """Add LLM-found skills only when they are (a) in the known vocabulary and
    (b) actually present as a token in the text. This keeps every skill grounded
    in real evidence — the model can never widen the set with invented skills.
    """
    lowered = text.lower()
    allowed_lower = {skill.lower() for skill in allowed_skills}
    for raw in llm_skill_names:
        name = raw.strip()
        if not name or name.lower() not in allowed_lower or name in parsed.skills:
            continue
        span = next(_iter_alias_spans(lowered, name.lower()), None)
        if span is None:
            continue  # not grounded in the text -> drop it
        parsed.skills.append(name)
        parsed.evidence[name] = [_evidence_snippet(text, span[0], span[1])]
    parsed.skills.sort()
    return parsed


def _clean_str_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def ground_ai_insight(
    raw: dict[str, Any],
    text: str,
    detected_skills: set[str],
    allowed_skills: set[str],
) -> ResumeAiInsight | None:
    """Re-verify the LLM analyst output against the resume before trusting it.

    - ``strongest_skills`` are filtered to skills the deterministic engine actually
      detected (so the model cannot promote skills the candidate never stated).
    - ``high_upside_skills`` are filtered to the known market vocabulary, excluding
      skills already held (recommendations stay grounded in real app data).
    - every evidence ``quote`` must appear verbatim in the resume; non-matches drop.

    Returns ``None`` when nothing survives grounding, so the UI falls back cleanly.
    """
    if not isinstance(raw, dict):
        return None

    detected_lower = {skill.lower() for skill in detected_skills}
    allowed_lower = {skill.lower() for skill in allowed_skills}

    def _dedupe(names: list[str], keep: set[str], exclude: set[str] = frozenset()) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for name in names:
            key = name.lower()
            if key in keep and key not in exclude and key not in seen:
                seen.add(key)
                out.append(name)
        return out

    strongest = _dedupe(_clean_str_list(raw.get("strongest_skills")), detected_lower)[:5]
    upside = _dedupe(
        _clean_str_list(raw.get("high_upside_skills")), allowed_lower, exclude=detected_lower
    )[:5]

    def _norm(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    normalised_text = _norm(text).lower()
    evidence: list[ResumeEvidenceQuote] = []
    raw_evidence = raw.get("evidence")
    if isinstance(raw_evidence, (list, tuple)):
        for item in raw_evidence:
            if not isinstance(item, dict):
                continue
            quote = _norm(str(item.get("quote", "")))
            if quote and quote.lower() in normalised_text:  # verbatim only
                evidence.append(ResumeEvidenceQuote(skill=str(item.get("skill", "")).strip(), quote=quote))
            if len(evidence) >= 5:
                break

    summary = _norm(str(raw.get("summary", "")))[:600]
    role_fit = _norm(str(raw.get("role_fit", "")))[:300]
    next_moves = [move[:240] for move in _clean_str_list(raw.get("next_moves"))][:3]

    if not (summary or strongest or upside or role_fit or next_moves or evidence):
        return None

    return ResumeAiInsight(
        mode="ai_assisted",
        model=str(raw.get("model")) if raw.get("model") else None,
        summary=summary,
        strongest_skills=strongest,
        high_upside_skills=upside,
        role_fit=role_fit,
        next_moves=next_moves,
        evidence=evidence,
    )


def merge_llm_skills_with_deterministic(
    deterministic: list[str],
    llm: list[str],
    allowed_skills: set[str],
) -> list[str]:
    """Merge LLM-suggested skills into deterministic ones, failing closed.

    Only skills present in ``allowed_skills`` (the known market vocabulary) are
    admitted, so the model can never invent credentials, employers, or skills.
    """
    allowed_lower = {skill.lower() for skill in allowed_skills}
    merged = list(deterministic)
    seen = {skill.lower() for skill in deterministic}
    for skill in llm:
        key = skill.lower()
        if key in allowed_lower and key not in seen:
            merged.append(skill)
            seen.add(key)
    return merged
