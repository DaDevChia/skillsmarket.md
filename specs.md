# SkillsMarket Full Build Specification

## 0. Status

**Project:** SkillsMarket, product name **SkillsMarket**  
**Public hostname:** `https://skillsmarket.onrender.com`  
**Working directory:** `/home/claude_code/skillsmarket`  
**Spec owner:** Hermes coordinator agent  
**Build mode:** local-first app, Cloudflare Tunnel for public egress

This file is the canonical implementation spec for the hackathon build.

Source material consulted:

- `skillsmarket.md`, original product/technical PRD.
- `UNDERSTANDING.md`, interpreted product summary.
- `STACK_AND_DATA.md`, stack and source plan.
- `API_REQUIREMENTS_AND_APIFY.md`, API/source/key plan.
- `SETUP_STATUS.md`, verified credentials and environment.
- `cloudflare-tunnel.md`, public egress notes.

Note: I searched the project folder for a pre-existing Claude/Codex workflow document. None was present before this file. This spec therefore defines the Claude/Codex workflow requested in the voice note and should be treated as the workflow reference unless a newer dedicated file is added.

---

## 1. Product summary

SkillsMarket is a Singapore skills exchange. It prices skills like market securities using labour-market demand and competition signals, normalises prices to a national baseline, and turns career anxiety into one explainable learning action.

The judge-facing summary:

> SkillsMarket prices Singapore's skills like a stock-market index, shows whether your career portfolio is appreciating or depreciating against the national baseline, and recommends the single subsidised course that most improves your Career Index.

The product must feel like:

- Bloomberg terminal for your career.
- S&P 500 for skills.
- Gov-safe employability index, not crypto, gambling, or social ranking.

The primary persona for the demo is:

> Mdm Lim, 47, retrenched admin executive, considering a transition from admin-heavy work into data-enabled operations.

---

## 2. Non-negotiable product rules

1. Headline value is always **index points**, never dollars.
2. Salary appears only as a secondary credibility signal.
3. No betting, no wagering, no fake token, no person-vs-person leaderboard.
4. Every recommendation must be explainable from source data or clearly labelled as seeded/curated.
5. MyCareersFuture direct public API is the authoritative pricing feed.
6. Apify private-board sources are secondary triangulation only.
7. The demo must work from cached data without relying on live APIs on stage.
8. The UI must funnel from market signal to concrete action, not drown the user in a 3,666-skill spreadsheet. A spreadsheet with lipstick remains a spreadsheet.

---

## 3. Technical stack

### 3.1 Frontend

- Vite.
- React.
- TypeScript.
- Tailwind CSS.
- Recharts or custom SVG for charts.
- Playwright for end-to-end testing.

### 3.2 Backend

- Python 3.11.
- FastAPI.
- Pydantic.
- Polars for analytics, pandas fallback if needed.
- Uvicorn for local server.
- Pytest for backend tests.

### 3.3 Data/cache

- Local JSON/Parquet snapshots.
- SQLite optional only if needed for history and snapshot metadata.
- No remote database for MVP.

Directory convention:

```text
data/raw/
```

```text
data/processed/
```

```text
data/fixtures/
```

```text
data/cache/
```

Generated data folders are ignored by git unless explicitly curated fixtures are placed under `data/fixtures`.

### 3.4 Public egress

Local app exposed via Cloudflare Tunnel.

```text
https://skillsmarket.onrender.com
```

Local backend:

```text
http://127.0.0.1:8000
```

Local frontend:

```text
http://127.0.0.1:5173
```

Preferred public routing:

```text
skillsmarket.onrender.com -> local frontend
```

Frontend proxies:

```text
/api/* -> http://127.0.0.1:8000/api/*
```

---

## 4. Secrets and external services

Secrets live in `.env`, never in git.

Configured and verified:

```text
APIFY_TOKEN
```

```text
APIFY_USER_ID
```

```text
OPENROUTER_API_KEY
```

```text
OPENROUTER_MODEL=openai/gpt-5.4-mini
```

```text
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

```text
SKILLSMARKET_PUBLIC_HOSTNAME=skillsmarket.onrender.com
```

OpenRouter caveat:

```text
max_tokens must be >= 16
```

The LLM is allowed to explain engine outputs, rewrite recommendation copy, and help convert structured facts into plain English. It is not allowed to invent prices, sources, courses, costs, or provenance.

---

## 5. Data sources

### 5.1 Authoritative price feed: MyCareersFuture direct API

Use the public endpoint directly:

```text
https://api.mycareersfuture.gov.sg/v2/jobs
```

Required fields:

| Field | Use |
|---|---|
| `results[].skills[].skill` | skill demand count |
| `results[].skills[].uuid` | stable skill identifier when available |
| `results[].skills[].isKeySkill` | key-skill weighting |
| `results[].metadata.totalNumberJobApplication` | supply/competition proxy |
| `results[].salary.minimum` | secondary wage-premium signal |
| `results[].salary.maximum` | secondary wage-premium signal |
| `results[].categories[]` | sector rollup |
| `results[].positionLevels[]` | seniority rollup |
| `results[].ssocCode` | future structural joins |
| `results[].metadata.newPostingDate` | trend/snapshot metadata |
| `expiryDate` | active-posting validity |

MVP ingestion behaviour:

1. Pull a bounded number of pages for development.
2. Save raw snapshot to `data/raw/mycareersfuture/<timestamp>.json`.
3. Create a named base-date snapshot.
4. Compute frozen divisor from that snapshot.
5. Use cached snapshot for demos.

### 5.2 SkillsFuture taxonomy

Source:

```text
https://jobsandskills.skillsfuture.gov.sg/skills-frameworks#download-the-latest-skills-framework-dataset
```

Use these downloadable assets if accessible:

1. Unique Skills List.
2. Skills Framework Dataset across 38 sectors.
3. TSC to Unique Skills Mapping File.

MVP behaviour:

- Load official taxonomy when available.
- Curate mapping for demo persona if full mapping takes too long.
- Clearly label fuzzy mapping.

### 5.3 Apify secondary sources

Budget is approved for Apify. Use Apify for secondary/private-market triangulation, not for the authoritative SkillsMarket price.

Priority actors:

```text
memo23/jobstreet-scraper
```

```text
valig/indeed-jobs-scraper
```

```text
orgupdate/google-jobs-scraper
```

Optional:

```text
agentx/all-jobs-scraper
```

Fallback only:

```text
jungle_synthesizer/mycareersfuture-jobs-scraper
```

Secondary source UI label:

> Private-board demand check, not used in official SkillsMarket price.

### 5.4 data.gov.sg structural sources

No key required.

API pattern:

```text
https://data.gov.sg/api/action/datastore_search?resource_id={dataset_id}
```

Candidate datasets:

```text
d_f8940ce770d7506567a7579712eedff2
```

```text
d_e86bfae75632429f22fb315adba3e1a3
```

```text
d_67b046947152332da235ad4353673a37
```

```text
d_ecba92f3eb2e32da9625a7ab97164109
```

```text
d_d2518fed6cc2014f0cd061b4570a9592
```

Use in MVP only if cheap. Otherwise present as Phase 2 structural calibration.

### 5.5 Course data

Preferred:

- SSG-WSG course APIs, if accessible.

Fallback:

- Curated demo course rows with explicit provenance.

Each course row must include:

| Field | Required |
|---|---:|
| course title | yes |
| provider | yes |
| mapped skill | yes |
| duration | yes |
| cost/subsidy label | yes, can be curated |
| enrolment URL | yes, can be placeholder if labelled |
| provenance | yes |

---

## 6. Index model

### 6.1 Skill price

```text
raw_score(skill) = weighted_demand(skill) / supply_proxy(skill)
```

```text
price(skill) = raw_score(skill) / frozen_divisor
```

The divisor is solved once on the base snapshot:

```text
median skill price = 100
```

### 6.2 Demand

Demand is active postings tagged with the skill, weighted by key-skill status.

Default weights:

| Skill tag | Weight |
|---|---:|
| `isKeySkill=true` | 1.5 |
| `isKeySkill=false` | 1.0 |

### 6.3 Supply proxy

Supply proxy is applicant competition from MyCareersFuture:

```text
metadata.totalNumberJobApplication
```

Use average applications across postings containing that skill for MVP, with robustness guards:

- missing application count -> 1,
- zero application count -> 1,
- extreme application count -> optional winsorisation after inspection.

### 6.4 De-noising

Required before the board is judge-visible:

1. Minimum support threshold.
2. Soft-skill stoplist/downweighting.
3. IDF-style rarity adjustment if soft-skill stoplist is too blunt.
4. Official taxonomy mapping where available.
5. Human-readable provenance for every derived number.

### 6.5 Sector index

Sector indices are demand-weighted averages of constituent skill prices.

```text
sector_index = sum(skill_price * skill_demand_weight) / sum(skill_demand_weight)
```

### 6.6 Career Index

Career Index is the demand-weighted average of skills in a user's portfolio.

For Mdm Lim MVP:

Initial holdings should include admin-heavy skills:

- Microsoft Excel.
- Administration.
- Scheduling / operations coordination.
- Customer service.
- Communication.

Target role should include data-enabled operations skills:

- Data Analysis.
- Data Storytelling.
- Python basics or no-code analytics.
- Workflow automation.
- AI-assisted operations.

---

## 7. Backend API requirements

### 7.1 Existing endpoints

```text
GET /api/health
```

```text
GET /api/market/skills
```

```text
GET /api/market/sectors
```

### 7.2 Required MVP endpoints

```text
GET /api/snapshots
```

Returns cached snapshots and which one is the base-date snapshot.

```text
POST /api/ingest/mycareersfuture
```

Pulls bounded pages from MyCareersFuture and writes raw cache.

```text
POST /api/ingest/apify/{source}
```

Runs a configured Apify actor for secondary demand validation.

```text
POST /api/index/recompute
```

Recomputes market output from a selected snapshot.

```text
GET /api/market/skills
```

Returns sorted skill board.

```text
GET /api/market/sectors
```

Returns sector indices.

```text
GET /api/personas/mdm-lim
```

Returns Mdm Lim role, holdings, Career Index, target role, and weak/strong skills.

```text
POST /api/simulate-trade
```

Input: persona ID plus candidate skill/course.  
Output: before/after Career Index, point delta, explanation, and course provenance.

```text
POST /api/shocks/genai
```

Applies a deterministic demo shock:

- admin demand down,
- AI/data/automation demand up,
- divisor unchanged.

```text
GET /api/explain/skill/{skill_id}
```

Returns structured explanation:

- price,
- demand,
- supply proxy,
- divisor,
- source rows count,
- key-skill contribution,
- provenance label.

```text
POST /api/explain/llm
```

Uses OpenRouter to rewrite a structured explanation in plain English.

Guardrail:

- If structured facts are missing, return an error. Do not hallucinate.

---

## 8. Frontend behaviour

### 8.1 Overall look

Visual direction:

- Dark Bloomberg-terminal inspired UI.
- High contrast, dense but readable.
- Singapore gov-safe polish, not meme-finance casino.
- Accent colours: green for rising, red for falling, amber for warnings, cyan/blue for data provenance.
- Use points as the primary unit everywhere.

Tone:

- Confident.
- Practical.
- Explanatory.
- Light market metaphor, never gambling.

### 8.2 Main layout

Desktop layout:

1. Top navbar.
2. Big Board ticker strip.
3. Three-column hero dashboard:
   - left: sector indices,
   - centre: personal Career Index card,
   - right: recommendation/trade card.
4. Skill board table.
5. Provenance panel.
6. Shock simulator panel.

Mobile layout:

- Stack hero cards.
- Ticker remains horizontally scrollable.
- Tables collapse into cards.

### 8.3 Page sections

#### Hero

Must show:

```text
The Singapore Skills Exchange
```

Subtitle:

```text
A Bloomberg terminal for your career.
```

Primary KPI:

```text
Career Index 94.0
```

Comparison:

```text
National baseline: 100
```

```text
Tech sector: 128
```

#### Big Board ticker

A scrolling ticker of skills/sectors:

```text
PYTHON 185 ▲12.4
```

```text
EXCEL 92 ▼8.1
```

Each ticker item opens the skill explanation modal.

#### Skill board

Columns:

| Column | Meaning |
|---|---|
| Symbol | generated short ticker |
| Skill | canonical skill name |
| Price | points |
| Change | demo/current movement |
| Demand | postings/key-weighted count |
| Supply proxy | applications/competition |
| Sector | sector mapping |
| Provenance | real/proxied/seeded |

#### Personal portfolio

Mdm Lim card includes:

- current role,
- current holdings,
- Career Index,
- underperforming skills,
- target role,
- recommended trade.

#### Simulate-the-trade modal

Required copy shape:

```text
Acquire Data Storytelling
```

```text
Course: Data Storytelling for Business Operations
```

```text
Projected Career Index: 94 -> 113 (+19 pts)
```

```text
Why: Data Storytelling is scarce in admin-adjacent operations roles and improves your target-role overlap.
```

Must show cost/provenance:

```text
Course row: curated demo (styled after SkillsFuture; not SkillsFuture-sourced)
```

#### Shock simulator

Button:

```text
GenAI breakthrough
```

On click:

- show short animation,
- recalculate board with same frozen divisor,
- admin skills dip,
- AI/data/automation skills rise,
- show explanation: automation is modelled as demand shift, not black-box doom score.

#### Provenance panel

A small but visible table:

| Signal | Status | Source |
|---|---|---|
| Skill demand | Real | MyCareersFuture postings |
| Competition proxy | Real/proxy | MyCareersFuture applications |
| Salary | Real | Mandatory salary fields |
| Course mapping | Curated or API | SSG/SkillsFuture |
| Historical chart before base date | Seeded | Demo only |

---

## 9. End-to-end demo flow

The three-minute judge demo must support this path:

1. Open `skillsmarket.onrender.com`.
2. Big Board is already moving.
3. Select or show persona: Mdm Lim.
4. Show Career Index below national baseline.
5. Click Microsoft Excel/Admin skill explanation.
6. Open Simulate Trade.
7. Recommend Data Storytelling or Data Analysis course.
8. Show before/after Career Index uplift.
9. Click GenAI Shock.
10. Watch board reprice using same frozen divisor.
11. Close with provenance: real data, clear proxies, labelled seeded demo pieces.

---

## 10. Testing requirements

### 10.1 Backend tests

Use pytest.

Required coverage:

- price normalisation, median skill equals 100,
- key-skill weighting,
- missing/zero applications handled,
- minimum support threshold,
- soft-skill downweighting,
- sector index calculation,
- Career Index calculation,
- simulate-trade output,
- shock simulation keeps divisor constant,
- API endpoints return expected schema.

Run:

```bash
uv run pytest
```

### 10.2 Frontend tests

Use Playwright.

Install target:

```bash
npm install -D @playwright/test
```

Required E2E scenarios:

1. Home page loads and shows Big Board.
2. Skill ticker item opens explanation modal.
3. Mdm Lim persona card shows Career Index below 100.
4. Simulate Trade opens and shows before/after uplift.
5. GenAI Shock changes displayed prices without changing baseline.
6. Provenance panel is visible and labels real/proxy/seeded correctly.
7. `/api` failure state shows graceful error instead of blank dashboard.
8. Mobile viewport renders stacked cards and usable ticker.

Parallel test strategy:

- Split tests by page/feature file.
- Use Playwright workers.
- Avoid serial tests unless a scenario explicitly depends on state.
- Prefer deterministic fixture API mode for E2E.

Run:

```bash
npx playwright test --workers=4
```

For local visual debugging:

```bash
npx playwright test --headed
```

### 10.3 Smoke tests before public tunnel

```bash
curl -fsS http://127.0.0.1:8000/api/health
```

```bash
curl -fsS http://127.0.0.1:5173
```

```bash
curl -I https://skillsmarket.onrender.com
```

---

## 11. Git and patch workflow

### 11.1 Branching

If this folder is turned into a git repo, use feature branches:

```bash
git checkout -b feat/skillsmarket-mvp
```

For agent worktrees, prefer isolated worktrees:

```bash
git worktree add ../skillsmarket-claude feat/claude-frontend
```

```bash
git worktree add ../skillsmarket-codex feat/codex-review
```

If worktrees are not used, only one implementation agent may write files at a time.

### 11.2 Commit boundaries

Commit after each working vertical slice:

1. data ingestion slice,
2. index engine slice,
3. API slice,
4. frontend shell slice,
5. persona/trade slice,
6. shock simulator slice,
7. Playwright E2E slice,
8. Cloudflare tunnel/public smoke slice.

Commit message style:

```text
feat: add mycareersfuture snapshot ingestion
```

```text
test: add skill pricing engine coverage
```

```text
fix: preserve divisor during genai shock
```

```text
docs: add agent workflow spec
```

### 11.3 Patch rules

Before patching:

```bash
git status --short
```

After patching:

```bash
git diff --stat
```

```bash
git diff
```

Then run targeted tests, then full tests.

Patch acceptance gate:

- Tests pass.
- No secrets in diff.
- No generated raw cache committed.
- App still launches.
- UI requirement still satisfied.

### 11.4 Secret scanning

Before commits:

```bash
git diff --cached
```

Check that these never appear in tracked files:

```text
APIFY_TOKEN
```

```text
OPENROUTER_API_KEY
```

```text
CLOUDFLARED_TOKEN
```

The values may exist only in `.env` or local shell environment.

---

## 12. Claude/Codex agent workflow

### 12.1 Roles

Hermes is the coordinator.

Responsibilities:

- Own final spec.
- Split work into steps.
- Start and monitor external agents.
- Keep git clean.
- Run independent verification.
- Decide when work is acceptable.

Claude Code is the main implementation agent.

Primary responsibility:

- Frontend implementation.
- UX polish.
- React component structure.
- Integrating API responses into dashboard.
- Visual presentation and demo flow.

Codex is the adversarial implementation/review agent.

Primary responsibility:

- Challenge Claude's assumptions.
- Review backend and frontend correctness.
- Check tests and edge cases.
- Attack data/provenance claims.
- Propose fixes when Claude's implementation drifts from spec.

Codex may implement backend/data slices when useful, but its main value is adversarial review against Claude's work.

### 12.2 Goal-prompt requirement

When using Claude Code or Codex interactive sessions, prompt them with a self-contained task and then explicitly include:

```text
/goal <self-contained task prompt>
```

This is the operator signal that the agent should proceed on the supplied goal rather than merely plan.

### 12.3 Terminal session naming

Preferred tmux sessions:

```text
skillsmarket-claude
```

```text
skillsmarket-codex
```

Create Claude session:

```bash
tmux new-session -d -s skillsmarket-claude -c /home/claude_code/skillsmarket -x 160 -y 50 'claude'
```

Create Codex session:

```bash
tmux new-session -d -s skillsmarket-codex -c /home/claude_code/skillsmarket -x 160 -y 50 'codex'
```

Attach:

```bash
tmux attach -t skillsmarket-claude
```

```bash
tmux attach -t skillsmarket-codex
```

### 12.4 Claude prompt template

```text
You are Claude Code acting as the main frontend implementation agent for SkillsMarket.

Workdir: /home/claude_code/skillsmarket
Read first: specs.md, skillsmarket.md, STACK_AND_DATA.md, SETUP_STATUS.md.

Goal: implement the assigned frontend slice exactly as specified.

Rules:
- Use Vite + React + TypeScript + Tailwind.
- Do not touch .env or secrets.
- Do not invent data; consume backend APIs or deterministic fixtures.
- Preserve gov-safe market metaphor: index points, no gambling language.
- Add or update tests for your slice.
- Run the exact verification command given in this task.
- Final output must list changed files, commands run, and blockers.

Task: <INSERT TASK>

Verification:
<INSERT COMMANDS>

/goal Implement the assigned frontend slice above. Follow the rules and verification commands exactly.
```

### 12.5 Codex adversarial prompt template

```text
You are Codex acting as an adversarial review agent for SkillsMarket.

Workdir: /home/claude_code/skillsmarket
Read first: specs.md and the current git diff.

Goal: attack the implementation against the spec.

Review dimensions:
- Spec compliance.
- Data provenance honesty.
- Gov-safe wording.
- API/schema correctness.
- UI regression risk.
- Test quality.
- Secret leakage.
- Playwright coverage gaps.

Do not make broad rewrites unless explicitly assigned. Prefer specific findings with file paths and exact fixes.

Final output format:
- Critical issues.
- Important issues.
- Minor issues.
- Suggested patch plan.
- Verdict: APPROVED or REQUEST_CHANGES.

/goal Review the current implementation adversarially against specs.md and the current git diff. Return the requested verdict format.
```

### 12.6 Coordinator loop

For each implementation step:

1. Hermes prepares task prompt.
2. Claude implements the slice with `/goal <task prompt>`.
3. Hermes inspects diff and runs tests.
4. Codex reviews adversarially with `/goal <review prompt>`.
5. Hermes decides:
   - accept,
   - send back to Claude for fixes,
   - ask Codex for a narrow patch,
   - or patch directly only if trivial.
6. Hermes runs full verification.
7. Hermes commits the slice.

No slice is done because an agent says it is done. It is done when Hermes verifies it. Machines are very confident liars; this is why we have tests.

---

## 13. Implementation roadmap

### Step 1: Data acquisition and fixtures

Goal:

- Gather real/cached data and deterministic fixtures.

Tasks:

1. Implement direct MyCareersFuture ingestion.
2. Save raw snapshot.
3. Normalise fields into internal posting schema.
4. Add fixture subset for stable E2E tests.
5. Optionally run Apify JobStreet/Indeed/Google actors for secondary validation.
6. Document provenance of every dataset.

Verification:

```bash
uv run pytest tests/test_ingest*.py tests/test_index_engine.py
```

### Step 2: Index engine

Goal:

- Compute market prices, sector indices, and Career Index correctly.

Tasks:

1. Implement robust skill aggregation.
2. Apply key-skill weighting.
3. Add min-support and soft-skill de-noising.
4. Solve frozen divisor.
5. Compute sector indices.
6. Compute Career Index.
7. Add shock simulation that preserves divisor.

Verification:

```bash
uv run pytest tests/test_index_engine.py
```

### Step 3: Backend API

Goal:

- Expose all data needed by frontend.

Tasks:

1. Add persona endpoint.
2. Add simulate-trade endpoint.
3. Add shock endpoint.
4. Add explain endpoint.
5. Add LLM rewrite endpoint with guardrails.
6. Add schema tests.

Verification:

```bash
uv run pytest tests/test_api.py
```

### Step 4: Frontend shell

Goal:

- Build visual dashboard skeleton.

Tasks:

1. Create Vite app.
2. Configure Tailwind.
3. Add API client.
4. Build dark terminal layout.
5. Add Big Board ticker.
6. Add market cards.
7. Add responsive layout.

Verification:

```bash
npm run build
```

### Step 5: Persona and trade flow

Goal:

- Make Mdm Lim demo complete.

Tasks:

1. Build persona card.
2. Build holdings list.
3. Show Career Index vs baseline.
4. Build recommendation card.
5. Build trade modal.
6. Show before/after uplift.
7. Show course provenance.

Verification:

```bash
npx playwright test tests/e2e/persona-trade.spec.ts --workers=4
```

### Step 6: Shock simulator

Goal:

- Make the market-event moment work.

Tasks:

1. Add GenAI shock button.
2. Trigger backend shock endpoint.
3. Animate changed skill prices.
4. Explain frozen divisor.
5. Add reset button.

Verification:

```bash
npx playwright test tests/e2e/shock.spec.ts --workers=4
```

### Step 7: Playwright full E2E

Goal:

- Prove the whole app behaves under browser automation.

Tasks:

1. Add Playwright config.
2. Add parallel E2E specs.
3. Add API mocking/fixture mode if needed.
4. Add screenshot-on-failure.
5. Add smoke test for public URL.

Verification:

```bash
npx playwright test --workers=4
```

### Step 8: Cloudflare public demo

Goal:

- Public site works on `skillsmarket.onrender.com`.

Tasks:

1. Run backend.
2. Run frontend.
3. Configure or run Cloudflare Tunnel.
4. Smoke test public hostname.
5. Test demo flow from public URL.

Verification:

```bash
curl -I https://skillsmarket.onrender.com
```

```bash
npx playwright test --config playwright.public.config.ts --workers=4
```

---

## 14. Definition of done

The MVP is done when:

- backend tests pass,
- frontend builds,
- Playwright E2E passes,
- Big Board is visible,
- Mdm Lim flow works,
- skill explanation modal works,
- simulate-trade works,
- GenAI shock works,
- provenance panel is visible,
- public Cloudflare URL works,
- no secrets are committed,
- README has run instructions,
- final demo can be executed in under three minutes.

Final full verification command set:

```bash
uv run pytest
```

```bash
npm run build
```

```bash
npx playwright test --workers=4
```

```bash
curl -I https://skillsmarket.onrender.com
```

---

## 15. Immediate next tasks

1. Implement MyCareersFuture ingestion and fixture normalisation.
2. Expand engine tests for de-noising, Career Index, simulate-trade, and shocks.
3. Create Vite frontend.
4. Assign Claude the frontend shell with `/goal <frontend task prompt>`.
5. Assign Codex adversarial review after Claude's first slice with `/goal <review prompt>`.
6. Keep Hermes as coordinator and independent verifier.
