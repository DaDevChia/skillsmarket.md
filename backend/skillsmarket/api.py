from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from skillsmarket.apify_sources import actor_for_source
from skillsmarket.data_sources import (
    BASELINE_EXPLAINER,
    DATA_LIMITS,
    DATA_SOURCES,
    PIPELINE_STAGES,
    PROVENANCE_ROWS,
)
from skillsmarket.engine import (
    apply_market_shock,
    compute_career_index,
    compute_market,
    explain_skill,
    recommended_trades,
    simulate_trade,
)
from skillsmarket.fixtures import COURSES, PERSONAS, demo_postings
from skillsmarket.ingest import ingest_mycareersfuture, list_snapshots, load_snapshot
from skillsmarket.ingest_apify import run_actor_and_fetch
from skillsmarket.extract import (
    ResumeExtractionError,
    UnsupportedResumeFormat,
    extract_resume_text,
)
from skillsmarket.llm import (
    analyze_resume_with_openrouter,
    explain_with_openrouter,
    research_skill_with_openrouter,
)
from skillsmarket.resume import (
    ResumeAnalysis,
    analyze_resume_text,
    enrich_parsed_with_llm,
    ground_ai_insight,
    parse_resume_text,
)
from skillsmarket.resume_examples import RESUME_EXAMPLES
from skillsmarket.history import attach_market_extras
from skillsmarket.live_evidence import (
    evidence_for_skill,
    latest_live_snapshot,
    live_market_or_none,
    load_evidence,
)
from skillsmarket.skill_catalog import augment_market_with_catalog
from skillsmarket.skill_detail import build_skill_detail
from skillsmarket.skillsfuture import courses_for_skill, load_courses
from skillsmarket.settings import settings

app = FastAPI(title="SkillsMarket", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        f"https://{settings.public_hostname}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestRequest(BaseModel):
    pages: int = Field(default=0, ge=0, le=20)
    limit: int = Field(default=100, ge=1, le=100)


class ApifyIngestRequest(BaseModel):
    max_items: int = Field(default=100, ge=1, le=10_000)
    keyword: str = "data analyst"
    location: str = "Singapore"
    wait_for_finish: int = Field(default=10, ge=0, le=120)


class RecomputeRequest(BaseModel):
    snapshot_id: str | None = None


class TradeRequest(BaseModel):
    persona_id: str = "mdm-lim"
    target_skill: str = "Data Storytelling"


class LlmExplainRequest(BaseModel):
    structured_facts: dict[str, Any]


class ResumeTextRequest(BaseModel):
    text: str = Field(min_length=20, max_length=50_000)


class ManualSkillsRequest(BaseModel):
    skills: list[str] = Field(min_length=1, max_length=60)


class SkillResearchRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)


def current_postings(snapshot_id: str | None = None) -> list[dict[str, Any]]:
    records, _snapshot = load_snapshot(snapshot_id)
    return records or demo_postings()


def active_snapshot_info() -> dict[str, Any]:
    """Honest snapshot descriptor, gated on the live-snapshot setting so seeded
    mode (tests/dev) never reports the on-disk live sweep."""
    if settings.use_live_snapshot:
        path = latest_live_snapshot()
        if path is not None:
            try:
                payload = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                payload = {}
            return {
                "snapshot_id": path.stem,
                "kind": "direct-public-api",
                "record_count": len(payload.get("records") or []),
                "created_at": payload.get("created_at"),
            }
    return {
        "snapshot_id": "fixture-base-2026-06-24",
        "kind": "fixture",
        "record_count": len(demo_postings()),
        "created_at": None,
    }


def current_market(snapshot_id: str | None = None) -> dict[str, Any]:
    # Live mode: real salary-priced MyCareersFuture market (real_proxy) + catalogue
    # for breadth. Seeded mode (default/tests): deterministic fixture only — the
    # on-disk live snapshot is deliberately ignored so personas/tests stay stable.
    if settings.use_live_snapshot:
        live = live_market_or_none()
        if live:
            return attach_market_extras(augment_market_with_catalog(live))
    market = compute_market(demo_postings(), min_support=1, provenance="seeded")
    return attach_market_extras(augment_market_with_catalog(market))


def persona_payload(persona_id: str) -> dict[str, Any]:
    persona = PERSONAS.get(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    market = current_market()
    career_index = compute_career_index(market, persona["holdings"])
    recommendations = recommended_trades(persona, market, COURSES)
    weak = [component for component in career_index["components"] if component["price"] < 100]
    strong = [component for component in career_index["components"] if component["price"] >= 100]
    return {
        **persona,
        "career_index": career_index,
        "weak_skills": weak,
        "strong_skills": strong,
        "recommendations": recommendations,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "skillsmarket"}


@app.get("/api/snapshots")
def snapshots() -> dict[str, Any]:
    active = active_snapshot_info()
    return {"active_snapshot": active, "snapshots": [active]}


@app.post("/api/ingest/mycareersfuture")
def ingest_mcf(request: IngestRequest) -> dict[str, Any]:
    result = ingest_mycareersfuture(pages=request.pages, limit=request.limit)
    return {k: v for k, v in result.items() if k != "records"} | {"record_count": result["record_count"]}


@app.post("/api/ingest/apify/{source}")
def ingest_apify(source: str, request: ApifyIngestRequest) -> dict[str, Any]:
    try:
        actor = actor_for_source(source)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if not settings.apify_token:
        raise HTTPException(status_code=503, detail="APIFY_TOKEN is not configured")
    actor_input = {"keyword": request.keyword, "location": request.location, "maxItems": request.max_items}
    url = f"https://api.apify.com/v2/acts/{quote(actor, safe='')}/runs"
    params = {"token": settings.apify_token, "waitForFinish": request.wait_for_finish}
    try:
        with httpx.Client(timeout=max(30, request.wait_for_finish + 10)) as client:
            response = client.post(url, params=params, json=actor_input)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Apify actor run failed: {exc}") from exc
    return {
        "mode": "apify-run",
        "source": source,
        "actor": actor,
        "input": actor_input,
        "run": payload.get("data", payload),
        "message": "Secondary validation actor started; authoritative price feed remains MyCareersFuture direct API.",
    }


@app.post("/api/ingest/apify/{source}/sweep")
def ingest_apify_sweep(source: str, request: ApifyIngestRequest) -> dict[str, Any]:
    """Run a configured Apify actor and return normalised, apify-labelled results.

    Bounded by max_items to respect the free plan. For a comprehensive multi-board
    sweep, raise max_items on a paid plan and call across sources."""
    if not settings.apify_token:
        raise HTTPException(status_code=503, detail="APIFY_TOKEN is not configured")
    try:
        return run_actor_and_fetch(
            source,
            keyword=request.keyword,
            location=request.location,
            max_items=request.max_items,
            wait_for_finish=request.wait_for_finish,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Apify sweep failed: {exc}") from exc


@app.post("/api/index/recompute")
def recompute_index(request: RecomputeRequest | None = None) -> dict[str, Any]:
    snapshot_id = request.snapshot_id if request else None
    _records, snapshot = load_snapshot(snapshot_id)
    market = current_market(snapshot["snapshot_id"])
    return {"status": "ok", "snapshot": snapshot, "market": market}


@app.get("/api/market/skills")
def market_skills() -> dict[str, Any]:
    market = current_market()
    return {"baseline": market["baseline"], "divisor": market["divisor"], "skills": market["skills"]}


@app.get("/api/market/sectors")
def market_sectors() -> dict[str, Any]:
    market = current_market()
    return {"baseline": market["baseline"], "sectors": market["sectors"]}


@app.get("/api/market/summary")
def market_summary() -> dict[str, Any]:
    market = current_market()
    persona = persona_payload("mdm-lim")
    active = active_snapshot_info()
    data_mode = "real_proxy" if active.get("kind") == "direct-public-api" else "seeded"
    return {
        "baseline": market["baseline"],
        "divisor": market["divisor"],
        "skills": market["skills"],
        "sectors": market["sectors"],
        "persona": persona,
        "recommendations": persona["recommendations"],
        "provenance": PROVENANCE_ROWS,
        "data_sources": DATA_SOURCES,
        "pipeline": PIPELINE_STAGES,
        "limits": DATA_LIMITS,
        "baseline_explainer": BASELINE_EXPLAINER,
        "snapshot": active,
        "data_mode": data_mode,
        "ingestion": _ingestion_meta(),
    }


def _ingestion_meta() -> dict[str, Any]:
    """Honest, real ingestion status read from the on-disk caches."""
    evidence = load_evidence()
    courses = load_courses()
    return {
        "mycareersfuture": (
            {
                "jobs": evidence.get("job_count"),
                "skills": len(evidence.get("skills", {})),
                "fetched_at": evidence.get("fetched_at"),
            }
            if evidence
            else None
        ),
        "skillsfuture": (
            {
                "courses": courses.get("course_count"),
                "matched_skills": len(courses.get("skills", {})),
                "fetched_at": courses.get("fetched_at"),
                "dataset_id": courses.get("dataset_id"),
            }
            if courses
            else None
        ),
    }


@app.get("/api/personas/{persona_id}")
def persona(persona_id: str) -> dict[str, Any]:
    return persona_payload(persona_id)


@app.post("/api/simulate-trade")
def simulate(request: TradeRequest) -> dict[str, Any]:
    persona = PERSONAS.get(request.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    try:
        return simulate_trade(persona, current_market(), COURSES, request.target_skill)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/shocks/genai")
def genai_shock() -> dict[str, Any]:
    shocked = apply_market_shock(current_postings(), base_market=current_market(), shock_name="genai")
    # Catalogue skills are seeded and unaffected by the demand shift; keep them on
    # the board (with sparkline/badges) so the full universe stays visible.
    return attach_market_extras(augment_market_with_catalog(shocked))


@app.get("/api/explain/skill/{skill_name}")
def explain(skill_name: str) -> dict[str, Any]:
    try:
        return explain_skill(current_market(), skill_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Skill not found") from exc


@app.post("/api/explain/llm")
def llm_explain(request: LlmExplainRequest) -> dict[str, Any]:
    try:
        return explain_with_openrouter(request.structured_facts)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/resume/examples")
def resume_examples() -> dict[str, Any]:
    return {
        "examples": [
            {"id": example.id, "label": example.label, "role": example.role}
            for example in RESUME_EXAMPLES
        ]
    }


def _analyze(text: str, source: str) -> ResumeAnalysis:
    """Analyse resume text with the deterministic engine, then layer a grounded
    LLM 'AI analyst' readout on top when OPENROUTER_API_KEY is configured.

    Always fails closed: any LLM error (no key, network, malformed JSON) leaves the
    deterministic, text-grounded analysis untouched and ``analysis_mode`` stays
    ``deterministic``. The model can never widen the skill set or invent resume
    facts — skills are intersected with the known vocabulary and every quote is
    re-verified verbatim against the resume text.
    """
    market = current_market()
    allowed = {str(skill["name"]) for skill in market["skills"]}
    parsed = parse_resume_text(text)

    ai_raw: dict[str, Any] | None = None
    if settings.enable_llm_resume:
        try:
            ai_raw = analyze_resume_with_openrouter(text, sorted(allowed))
            if ai_raw:
                parsed = enrich_parsed_with_llm(parsed, text, ai_raw.get("skills") or [], allowed)
        except Exception:  # any LLM failure -> deterministic result stands
            ai_raw = None

    analysis = analyze_resume_text(text, market, source=source, parsed=parsed)

    if ai_raw:
        try:
            detected = {skill.name for skill in analysis.skills}
            insight = ground_ai_insight(ai_raw, text, detected, allowed)
            if insight is not None:
                analysis.ai = insight
                analysis.analysis_mode = "ai_assisted"
        except Exception:  # grounding failure -> keep deterministic readout
            pass
    return analysis


@app.post("/api/resume/analyze-text")
def resume_analyze_text(request: ResumeTextRequest) -> ResumeAnalysis:
    return _analyze(request.text, source="paste")


@app.post("/api/resume/analyze-skills")
def resume_analyze_skills(request: ManualSkillsRequest) -> ResumeAnalysis:
    cleaned = [skill.strip() for skill in request.skills if skill.strip()]
    if not cleaned:
        raise HTTPException(status_code=422, detail="List at least one skill.")
    # Synthesise a tiny document so the same evidence-highlighting pipeline runs.
    text = "Self-entered skills: " + ", ".join(cleaned) + "."
    return _analyze(text, source="manual")


@app.get("/api/skill/{skill_id}")
def skill_detail(skill_id: str) -> dict[str, Any]:
    try:
        return build_skill_detail(current_market(), skill_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Skill not found") from exc


@app.post("/api/skill/research")
def skill_research(request: SkillResearchRequest) -> dict[str, Any]:
    """Add/look up a skill. If it's on the market, return its quote; otherwise
    auto-research it with the LLM (when enabled), clearly labelled as an estimate.
    Real SkillsFuture course matches are attached either way."""
    name = request.name.strip()
    market = current_market()
    lookup = {str(skill["name"]).lower(): skill for skill in market["skills"]}
    matched = lookup.get(name.lower())
    courses = courses_for_skill(name)
    if matched:
        return {
            "name": matched["name"],
            "on_market": True,
            "skill_id": matched["id"],
            "price": matched["price"],
            "sector": matched.get("sector"),
            "source_badges": matched.get("source_badges", []),
            "courses": courses,
            "research": None,
        }
    research = None
    if settings.enable_skill_research:
        try:
            research = research_skill_with_openrouter(name)
        except Exception:
            research = None
    return {
        "name": name,
        "on_market": False,
        "skill_id": None,
        "courses": courses,
        "research": research,
        "research_enabled": settings.enable_skill_research,
    }


@app.post("/api/resume/analyze-example/{example_id}")
def resume_analyze_example(example_id: str) -> ResumeAnalysis:
    example = next((row for row in RESUME_EXAMPLES if row.id == example_id), None)
    if not example:
        raise HTTPException(status_code=404, detail="Resume example not found")
    return _analyze(example.text, source=f"example:{example.id}")


@app.post("/api/resume/upload")
async def resume_upload(file: UploadFile = File(...)) -> ResumeAnalysis:
    filename = file.filename or "resume.txt"
    raw = await file.read()
    try:
        text = extract_resume_text(filename, raw)
    except UnsupportedResumeFormat as exc:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Upload TXT, PDF, or DOCX — or paste your resume text.",
        ) from exc
    except ResumeExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail="Could not read text from this file. Try another file or paste your resume text.",
        ) from exc
    if len(text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="This file had too little readable text. Paste your resume text instead.",
        )
    return _analyze(text, source=f"upload:{filename}")


# Render deployment serves the built Vite app from the same FastAPI process.
# In local development, Vite still owns the frontend and proxies /api to this app.
DIST_DIR = Path(__file__).resolve().parents[2] / "dist"
ASSETS_DIR = DIST_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    target = (DIST_DIR / full_path).resolve()
    if DIST_DIR.exists() and DIST_DIR.resolve() in target.parents and target.is_file():
        return FileResponse(target)
    index = DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse(
        {
            "status": "ok",
            "app": "skillsmarket",
            "message": "Frontend build not found. Run `npm run build` or use the Vite dev server.",
        }
    )
