# SkillsMarket

**A Bloomberg-style terminal for the Singapore skills market.** SkillsMarket prices skills like
market instruments — each skill gets an index value, a historical chart, source/provenance badges, a
plain-English methodology, real job evidence, and concrete next moves. Upload a resume (or key in your
own skills) and it reads back a personal Skill Index with AI-assisted, evidence-grounded analysis.

🔗 **Live:** https://skillsmarket.onrender.com &nbsp;·&nbsp; FastAPI + Vite/React &nbsp;·&nbsp; real MyCareersFuture + SkillsFuture data &nbsp;·&nbsp; OpenRouter LLM

---

## Highlights

- **Real Singapore data, honestly labelled.** Live sweep of the MyCareersFuture jobs API and ingestion
  of the official MySkillsFuture Course Directory — every number carries a source badge and a fetch date.
- **Two pricing modes.** A deterministic *seeded* index for stable demos/tests, and a *live* index priced
  on real median salary. The mode is shown in the header (`SEEDED SNAPSHOT` / `LIVE PROXY`).
- **Skill stock-analysis pages.** Interactive pan/zoom/range chart, real job postings (with links), real
  SkillsFuture courses, full rating breakdown, a confidence chip, and a GenAI shock scenario.
- **AI resume analyst.** Upload PDF/DOCX/TXT, paste, pick an example, or type your own skills. The LLM
  narrates a grounded readout — every quote is verbatim from your text and every skill is matched to the
  market; it never invents facts and fails closed to the deterministic engine.
- **Add any skill → live research.** Type a skill not on the board and the agent researches it live
  (sector, scarcity, salary estimate), clearly labelled *AI-researched estimate — not market data*.

---

## Pages

| Route | Purpose |
|---|---|
| `/` | Executive market overview — ticker, top quotes, 30-day movers, sector indices |
| `/resume` | Upload / paste / examples / **manual skill entry** → AI analyst workbench |
| `/skills` | Full searchable, sortable, sector-filterable market board (sparklines + source badges) |
| `/skills/:skill` | Individual skill stock-analysis (chart, live job evidence, courses, methodology) |
| `/methodology` | Full pricing & rating methodology — no black-box numbers |
| `/sources` | Data sources, live ingestion status, and the end-to-end pipeline |

Terminal/Bloomberg aesthetic throughout; every page stacks cleanly on mobile (no horizontal overflow).

---

## Data sources & provenance

SkillsMarket is deliberate about separating *original sources* from *ingestion infrastructure*:

| Source | Role | Status |
|---|---|---|
| **MyCareersFuture** (`/v2/search`) | Underlying job-demand & salary source | **Live sweep** (~1,160 real jobs) + seeded fallback |
| **MySkillsFuture Course Directory** (data.gov.sg `d_b5802b76…`) | Training-course recommendations | **Ingested** (~25,800 real courses) |
| **Apify** | Scraping / ingestion infrastructure (secondary validation) | Wired & tested; full sweep needs a paid plan |
| **OpenRouter** | LLM layer (resume analyst, add-skill research, explanations) | Live, grounded, fail-closed |
| **LinkedIn** | — | **Not ingested** (shown explicitly as not a source) |
| **Seeded fixture + skill catalogue** | Deterministic demo / fallback (~124 catalogue skills) | Labelled `seeded` everywhere |

**Pipeline:** `MyCareersFuture postings → Apify ingestion (optional) → SkillsMarket pricing engine → resume evidence matching → SkillsFuture course & action recommendations`

> **Honesty rules.** Apify is the collector, never the price. SkillsFuture is for courses, not pricing.
> Seeded data is never presented as live truth. Historical charts are deterministic **seeded backtests**,
> labelled as such — there is no real day-by-day price history yet.

---

## How prices are computed

Prices are **index values, not salaries**.

```text
100 = the median skill in the current snapshot.
Above 100 = scarcer / higher demand-to-supply (or higher pay, in live mode).
Below 100 = more common.
```

- **Seeded mode (default):** `price = (weighted_demand ÷ supply_proxy) ÷ frozen_divisor`, normalised so the
  median skill = 100. The divisor is frozen so shocked/future snapshots stay comparable.
- **Live mode:** the MyCareersFuture API returns sparse applicant counts, so the live index prices on
  **real median monthly salary** (median salary → 100) — the reliable job-money signal — with real
  posting counts as demand. This is stated plainly in the methodology and on every skill page.

Each skill exposes: demand score, supply/applicant proxy, salary/job-money proxy (where present), support
count, provenance, frozen divisor, baseline meaning, and a confidence level with explicit limitations.

---

## Local development

```bash
uv sync --all-groups        # Python deps (FastAPI, httpx, pypdf, python-docx, openpyxl, …)
npm install                 # Frontend deps (Vite, React, three.js, Playwright)
npx playwright install chromium
```

Run the backend and frontend:

```bash
PYTHONPATH=backend uv run uvicorn skillsmarket.api:app --host 127.0.0.1 --port 8000
npm run dev -- --port 5173
```

The Vite dev server proxies `/api/*` to the backend. Open http://127.0.0.1:5173.

### Refreshing the real data (optional)

```bash
PYTHONPATH=backend uv run python - <<'PY'
from skillsmarket.ingest_mcf import run_live_snapshot
from skillsmarket.live_evidence import build_evidence_aggregate, write_evidence
from skillsmarket.skillsfuture import download_course_rows, build_course_index, write_courses
from skillsmarket.skill_catalog import catalog_skill_names
import json, glob, os

run_live_snapshot(pages=2, limit=30)                                   # sweep MyCareersFuture
snap = sorted(glob.glob("data/raw/mycareersfuture/mcf-*.json"), key=os.path.getmtime)[-1]
write_evidence(build_evidence_aggregate(json.load(open(snap))["records"]))   # per-skill evidence cache
write_courses(build_course_index(catalog_skill_names(), download_course_rows()))  # SkillsFuture courses
PY
```

These write gitignored caches under `data/`. The live index turns on with `SKILLSMARKET_USE_LIVE_SNAPSHOT=true`.

---

## Configuration

Copy `.env.example` → `.env` (gitignored; never committed). Key flags:

| Variable | Default | Effect |
|---|---|---|
| `SKILLSMARKET_USE_LIVE_SNAPSHOT` | `false` | Price the market from the live MyCareersFuture salary sweep (`real_proxy`). Off keeps demos/tests deterministic. |
| `SKILLSMARKET_ENABLE_LLM_RESUME` | `true` | Auto AI resume analyst when `OPENROUTER_API_KEY` is set; fails closed to the deterministic engine. |
| `SKILLSMARKET_ENABLE_SKILL_RESEARCH` | `false` | Auto-research unknown skills on "Add a skill" (uses OpenRouter; per-call cost). |
| `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` | — | LLM provider + model. |
| `APIFY_TOKEN` | — | Apify secondary-validation sweeps (free plan is limited). |

In production these are set on the systemd backend unit; the public demo runs with live snapshot + skill
research enabled.

---

## Architecture

```text
backend/skillsmarket/
  api.py            FastAPI app + all endpoints; seeded vs live gating
  engine.py         pricing engine (demand/supply, frozen divisor, sectors, shock)
  skill_catalog.py  ~124 seeded skills across 16 SG domains (fallback / breadth)
  ingest_mcf.py     live MyCareersFuture /v2/search sweep
  live_evidence.py  per-skill real job evidence + salary-priced live market
  skillsfuture.py   MySkillsFuture Course Directory ingest (data.gov.sg)
  ingest_apify.py   Apify secondary-validation ingestion (built for a full sweep)
  resume.py         deterministic parser, highlights, rich actions, LLM grounding
  skill_detail.py   stock-analysis payload (history, methodology, confidence, evidence, courses)
  history.py        deterministic smoothed seeded backtest + sparklines
  llm.py            OpenRouter calls (resume analyst, skill research, explanations) — all fail closed

src/
  pages/            LandingPage, ResumePage, SkillsBoardPage, SkillDetailPage, MethodologyPage, SourcesPage
  components/       InteractiveChart, AiAnalystPanel, DocumentViewer, SortableSkillsList, AddSkillResearch, …
  router.tsx        tiny history-based router
```

---

## Verification

```bash
uv run pytest -q            # backend tests (deterministic; LLM stubbed offline)
npm run build              # type-check + production bundle
npx playwright test --workers=4   # E2E across chromium + mobile
```

Current status: **pytest ✓ · build ✓ · Playwright ✓** (chromium + mobile, including no-overflow checks).

Deployment configs for Render live in [`render.yaml`](render.yaml), [`Dockerfile`](Dockerfile), and
[`RENDER_DEPLOYMENT.md`](RENDER_DEPLOYMENT.md). The old Cloudflare Tunnel setup is local-demo only; Render
is preferred for public hosting so this machine is not the production server.

---

## Submission notes & HCI records

Submission answers and sanitised design-conversation records live in [`submissions/`](submissions/) and
[`submissions/human-computer-interaction/`](submissions/human-computer-interaction/). They preserve product
decisions and user feedback while removing credentials, raw resumes, and other sensitive material.

## License

MIT — see [`LICENSE`](LICENSE).
