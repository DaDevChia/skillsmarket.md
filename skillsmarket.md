# SkillsMarket — The Singapore Skills Exchange

### Product Requirements & Technical Spec (`skillsmarket.md`)

> A “Bloomberg terminal for your career.” SkillsMarket prices every skill in Singapore’s
> labour market using real supply-and-demand data, indexes it like a stock market,
> and turns “what should I learn next?” into a single, explainable, subsidised
> **trade** — enrol in the course that most raises your personal Career Index.

**Hackathon:** PyCon Singapore 2026 — Track 1: Job & Skills
**Filename:** `skillsmarket.md`
**Status:** Draft v1 (concept + MVP scope + data architecture)

-----

## 0. TL;DR for a judge (the 30-second version)

Singapore has world-class skills infrastructure (SkillsFuture credits, the Skills
Framework, MyCareersFuture) but an ordinary worker still can’t answer the only
question that matters: *“Is my skillset appreciating or depreciating, and what’s the
single best thing to learn next?”*

SkillsMarket answers it by treating skills as securities. Each skill is **priced by real
demand ÷ supply** from the live MyCareersFuture jobs API, indexed to a national
baseline (**median skill = 100**), and rolled up into sector indices and a personal
**Career Index**. The product then funnels you from “your index is below baseline”
to a **ranked, costed, subsidised learning pathway** — explainable down to the
dataset row. No fake money, no betting: it’s an *index*, the S&P 500 for skills.

-----

## 1. Problem & Insight

### 1.1 The problem

- Workers can’t see which of their skills are **rising or fading** in real demand.
- The Skills Framework is rich but unreadable (38 sectors of TSCs); MyCareersFuture
  lists jobs but not *trends*; credits go unspent because the value is opaque.
- Automation anxiety is abstract (“AI will take my job”) with no concrete signal of
  *which* skills are actually softening.

### 1.2 The insight

In labour economics, **the price of a skill is its scarcity** — where demand meets
supply. We don’t need to invent an “automation risk score”: automation shows up
**naturally as a demand-side shift** (postings requiring a skill fall → its price
falls). Modelling skills as a market is therefore *more* honest than a black-box
score, and it gives every recommendation a one-line, defensible explanation.

### 1.3 Why a market metaphor (and why it stays gov-safe)

The market framing is the **hook** (a ticker is fun, legible, memorable). It is kept
rigorous and non-degen by three rules (see §7):

1. Value = **employability/resilience**, never cash.
1. **No betting, no person-vs-person leaderboard.** Every CTA is “learn,” never “wager.”
1. It’s an **index** (points vs a national baseline), exactly like the S&P — a
   respected public economic instrument, not a casino.

-----

## 2. The Pricing Model (the core IP)

### 2.1 Unit: points, indexed to a national baseline

Every skill is quoted in **points**, not dollars. The number is concrete because it
is anchored to a fixed reference, exactly how real indices work (S&P base = 10 in
1941–43; Nasdaq base = 100 in 1971 — the base value is a costume, the **base period

- frozen divisor** is the anchor).

```
Price(skill) = ( Demand(skill) / Supply(skill) ) / Divisor

where Divisor is solved ONCE on the base date so that the
MEDIAN skill across the whole market = 100.
```

- **Above 100** → scarcer / more wanted than the typical Singaporean skill.
- **Below 100** → more crowded / fading vs the typical skill.
- The **divisor is frozen** after the base date, so future snapshots move *relative to
  the same fixed national benchmark* — this converts a single snapshot into a real
  time series without needing years of history.

### 2.2 What D and S actually are (MVP — single source, fully real)

Both computed from the **same** public MyCareersFuture endpoint, per skill:

|Term          |Definition                                                       |Field                                         |
|--------------|-----------------------------------------------------------------|----------------------------------------------|
|**Demand (D)**|# active postings tagged with the skill                          |`results[].skills[].skill`                    |
|**Supply (S)**|applicant competition for those postings (avg/total applications)|`results[].metadata.totalNumberJobApplication`|
|**Price**     |`(D / S)` normalised so median skill = 100                       |derived                                       |


> **Validated on live data (800 postings):** Microsoft Excel ≈ 140, generic soft
> skills balloon to 400–1400. This is *why* normalization + key-skill weighting
> matters (§2.4) — and it’s a great “we understand our data” talking point.

### 2.3 Secondary signal — salary premium (real, law-mandated)

Salary is **mandatory** on every posting (FAIR Consideration Framework), so we show a
secondary, hover-only signal: *“also commands ~1.8× the median wage.”* Never on the
main axis (keeps money off the ticker), but proves real economic value sits
underneath. Source: `results[].salary.minimum / .maximum`.

### 2.4 De-noising (required for the “actionable not overwhelming” rubric point)

Raw frequency over-weights filler skills (“Team Player”). The engine must:

- **Weight by `isKeySkill`** — core skills count more than peripheral tags.
- **Cap / down-weight generic soft skills** via a stoplist or an IDF-style rarity weight.
- **Min-support threshold** — ignore skills with < N postings (noise).
- Map raw skill strings → **Skills Framework TSCs** so the user sees recognised,
  framework-valid skills, not 3,666 raw tags.

### 2.5 Three-tier index structure (the S&P grammar)

```
  Currency:     points (base: median skill = 100, frozen divisor)
      │
  Securities:   individual SKILLS, each quoted in points
      │
  Indices:      SECTOR indices (Tech, Care, Green, Admin…) =
                demand-weighted avg of constituent skills
      │
  Personal:     YOUR CAREER INDEX = demand-weighted avg of skills you hold
                e.g. "Career Index 96.4 — below national 100, lagging Tech (128)"
      │
  The Exchange: SkillsMarket (the whole national board)
```

Sector indices use **demand-weighting** (bigger-demand skills move the index more),
mirroring S&P market-cap weighting — *not* Dow-style price-weighting (cruder).

### 2.6 The action loop (what makes it Track-1, not just a viz)

1. User enters current role → portfolio auto-populated from Skills Framework.
1. Career Index shown vs national baseline + target role.
1. Engine finds **undervalued, durable, subsidised** skills that most raise the index.
1. **“Simulate the trade”:** *“Acquire Data Storytelling (real subsidised course,
   $X after subsidy, 6 weeks) → Career Index +Y pts, automation exposure −Z%.”*
1. Real course + real cost + projected index impact → enrol.

> “Simulate the trade, then enrol” is the bridge from market-toy to SkillsFuture-real,
> and it satisfies *“offer actionable pathways instead of overwhelming skill sets.”*

-----

## 3. Data Sources & Provenance (the Data-Quality scorecard)

> **PyCon Track 1 weights “Data Quality” heavily. This honesty map is a first-class
> product feature and a pitch slide — show exactly which numbers are observed vs
> estimated vs cosmetic.** Most teams will hand-wave this; we won’t.

### 3.1 Tier 1 — Real & live (skill-level, daily) — MVP SPINE

**MyCareersFuture public API** — `https://api.mycareersfuture.gov.sg/v2/jobs`

- No auth, no key, ~**85,600** live postings, 100/page pagination.
- Fields used:

|Field                                                   |Use                                    |
|--------------------------------------------------------|---------------------------------------|
|`skills[].skill`, `skills[].uuid`, `skills[].isKeySkill`|Demand counts, ticker symbol, weighting|
|`metadata.totalNumberJobApplication`                    |**Supply / competition proxy**         |
|`salary.minimum`, `salary.maximum`                      |Secondary wage-premium signal          |
|`ssocCode`, `ssocVersion`                               |**Join key** to MOM labour-supply data |
|`categories[]`, `positionLevels[]`                      |Sector & seniority rollups             |
|`metadata.totalNumberOfView`                            |Bonus demand-interest signal           |
|`metadata.newPostingDate`, `expiryDate`                 |Time-windowing / trend                 |


> **Ingestion:** via **Apify** (sponsor — free $100 credit code `HACKSG`, plus a
> top-3 Apify prize). A ready MyCareersFuture actor exists hitting this exact API.
> Using Apify = free data + prize eligibility + a real, demonstrable pipeline.

### 3.2 Tier 1 — Backbone taxonomy — SkillsFuture Skills Framework dataset

Official downloadable dataset (38 sectors, quarterly), the **sanctioned** source
the track points to. Used to: map raw skill strings → TSCs, define sectors, populate
a user’s starting portfolio from their role.
Download: `https://jobsandskills.skillsfuture.gov.sg/skills-frameworks`

### 3.3 Tier 2 — Real & structural (sector-level, annual) — VISION / Phase 2

**data.gov.sg** uniform API: `https://data.gov.sg/api/action/datastore_search?resource_id={id}`
(no auth; 4,500+ datasets). Used to *calibrate* supply scale & elasticity:

|Dataset                             |resource_id                         |Role                                  |
|------------------------------------|------------------------------------|--------------------------------------|
|Labour Force Aged 15+               |`d_f8940ce770d7506567a7579712eedff2`|Worker-pool scale                     |
|Unemployed by Qualification/Duration|`d_e86bfae75632429f22fb315adba3e1a3`|Slack in supply                       |
|Residents by Highest Qualification  |`d_67b046947152332da235ad4353673a37`|Supply by education                   |
|Training Places Taken / Completed   |`d_ecba92f3eb2e32da9625a7ab97164109`|**Forward supply / value-trap signal**|
|Employment by Sector (SSIC)         |`d_d2518fed6cc2014f0cd061b4570a9592`|Sector employment base                |

Plus **SSOC 2024 search** (SingStat) to resolve `ssocCode` → occupation → SSIC sector.

### 3.4 Tier 3 — Seeded & clearly labelled

Intra-period **historical back-trend** for ticker motion. We launch with one base-date
snapshot, so any “past” curve before first run is **illustrative** and labelled as
such. (After the system runs over time, history becomes real.) Never presented as
observed truth.

### 3.5 The two-speed model (decision: build single-speed, pitch two-speed)

- **High-frequency engine (MVP, real):** live skill-level D/S from MyCareersFuture.
  This is what ticks and drives the demo.
- **Structural calibration (Phase 2, spec’d):** annual MOM/SingStat/WSQ data sets the
  per-sector baseline scale and the elasticity/“value-trap” haircut.
- Honest framing: *“high-frequency signal from live postings, structural calibration
  from national labour statistics”* — exactly how real indices blend fast market data
  with slow census benchmarks. **MVP ships single-source; the slide shows the vision.**

-----

## 4. MVP Scope (what we actually build)

### IN — MVP

1. **Ingestion** (Apify/Python): pull N pages of live MyCareersFuture postings → cache
   as the **base-date snapshot** (defines the frozen divisor; reproducible; no live
   stage risk).
1. **Index engine** (Python): aggregate D & S per skill → normalise (median = 100) →
   compute sector indices + Career Index. De-noise per §2.4. Map to TSCs.
1. **The Big Board**: scrolling ticker of skills/sectors, green/red, % change.
1. **Personal Portfolio**: enter role → holdings → Career Index vs baseline & target.
1. **Simulate-the-trade**: ranked subsidised courses → projected Career Index uplift,
   each recommendation **explained from dataset rows** (“142 = D 74 ÷ S 53, ×divisor”).
1. **Market-event demo button** (see §6): fire a shock, re-run through the *same
   divisor*, watch the board move live.

### OUT — Phase 2 / vision

- Live data.gov.sg structural calibration & elasticity haircut.
- Real longitudinal history; real SSOC→SSIC→MOM supply join.
- Skills passport write-back; employer/team aggregate view; auth & accounts.

-----

## 5. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  INGESTION (Python / Apify)                                       │
│   • MyCareersFuture actor → JSON → base-date snapshot (cached)    │
│   • SkillsFuture Framework dataset (static) → TSC taxonomy        │
│   • [Phase 2] data.gov.sg datastore_search → structural layer     │
└───────────────┬─────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  INDEX ENGINE (Python: pandas/Polars + FastAPI)                  │
│   • aggregate D (postings) & S (applications) per skill           │
│   • de-noise: isKeySkill weight, soft-skill cap, min-support      │
│   • map raw skill → Skills Framework TSC + sector                 │
│   • solve divisor so median skill = 100  → FREEZE                 │
│   • sector indices (demand-weighted) + Career Index               │
│   • "simulate trade": Δ Career Index from acquiring a skill       │
│   • market-event simulator (shift D for a skill cluster)          │
└───────────────┬─────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT LAYER (OpenAI API — sponsor stack)                         │
│   • NL explanation of any quote ("why is this 142?")              │
│   • role → starting portfolio; goal → ranked pathway              │
│   • plain-language coaching, grounded in engine outputs (no halluc)│
└───────────────┬─────────────────────────────────────────────────┘
                ▼
┌─────────────────────────────────────────────────────────────────┐
│  FRONTEND (Big Board ticker + Personal Portfolio + Trade modal)  │
└─────────────────────────────────────────────────────────────────┘
```

**Stack (tuned to PyCon sponsors & “Technical Execution”):**

- **Python** engine — FastAPI + pandas/Polars (it’s PyCon; the engine must be Python).
- **OpenAI API** for the agent/explanation layer (sponsor; free credits).
- **Apify** for ingestion (sponsor; free credits + prize).
- Frontend: lightweight (React/HTML + a charting lib); the engine is the substance.

-----

## 6. The Demo (3-minute pitch flow)

1. **Hook (15s):** “Is your career appreciating or depreciating? We built the S&P 500
   for Singapore’s skills.” Big Board scrolling live, green/red.
1. **One persona (45s):** *Mdm Lim, 47, retrenched admin executive.* Enter her role →
   Career Index **94, below the national 100**, lagging the Tech sector at 128. Her
   biggest holding (“MS Office”) is flashing red — crowded, fading.
1. **Explainability (30s):** click a skill → *“142 because 74 postings need it vs 53
   applicants, normalised to the median skill.”* Every number traces to a dataset row.
   Flash the **data-provenance slide** (real / proxied / seeded).
1. **The trade (45s):** “Simulate the trade” → top subsidised course (real, costed)
   lifts her Career Index from 94 → 113, automation exposure down. One click to enrol.
1. **The shock, live (30s):** press **“GenAI breakthrough”** → admin skills dip below
   100, AI-ops skills spike — *through the same frozen divisor*, so it’s a real,
   comparable move, not a cartoon. “Automation isn’t a scary score — it’s a demand
   shift, and we price it.”
1. **Vision (15s):** two-speed national index → SkillsMarket as public infrastructure WSG
   could run. Land the grand idea.

-----

## 7. Gov-Safe Guardrails (design rules, not afterthoughts)

- Value is always **employability/resilience**, expressed in index points — **never $**.
- **No wagering, no stakes, no person-vs-person leaderboard.** CTAs say *Learn*, never *Bet*.
- Framed as **(a) a personal balance sheet + (b) a national skills index** — prudent
  planning + civic data.
- Salary shown only as a secondary credibility signal, never the headline unit.
- Recommendations must be **explainable from the dataset** (it’s also a rubric line).
- Pitch line: *“We didn’t invent a fake coin. We built an index.”*

-----

## 8. Rubric Alignment (PyCon Track 1)

|Criterion                     |How SkillsMarket scores                                                                                                                                                         |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**Data Quality / Integrity**  |Real D *and* S from the live gov API; mandatory salary; sanctioned Skills Framework taxonomy; explicit real/proxied/seeded provenance map; honest two-speed model.         |
|**Technical Execution**       |Python index engine (normalisation, frozen-divisor maths, de-noising, sector rollups), live ingestion via Apify, OpenAI grounded-explanation layer, market-event simulator.|
|**Overall Experience & Value**|One persona, before/after Career Index, **every number explained**, funnels to a *small actionable* pathway not 3,666 skills, real subsidised courses.                     |
|**Process & Product**         |Clear problem → economic insight → working data pipeline → individual action loop; vision to national infrastructure.                                                      |
|**“What Good Products Do”**   |✓ explains recommendations from dataset logic · ✓ actionable pathways over overwhelming skill sets.                                                                        |
|**Sponsor alignment**         |OpenAI (agent) + Apify (ingestion, prize-eligible) + curated demo mappings styled after SkillsFuture (SkillsFuture data not currently ingested).                                                                                        |

-----

## 9. Open Decisions / Risks

- **Soft-skill noise** (validated real): must de-noise or the board looks silly →
  §2.4 is mandatory, not optional.
- **Supply proxy is competition, not headcount:** applications ≈ competition, a *proxy*
  for true labour supply. Be explicit; Phase 2 calibrates with MOM headcount.
- **API politeness:** cache a base-date snapshot; don’t hammer the endpoint live on stage.
- **TSC mapping fidelity:** raw skill strings → Framework TSCs is fuzzy; ship a curated
  mapping for the demo’s persona/sector, generalise later.
- **Naming:** product = **SkillsMarket / SG Skills Exchange**; personal rollup = **Career
  Index**; mid-tier = **Sector Indices**. (Filename stays `skillsmarket.md`.)

-----

## 10. One-line summary

**SkillsMarket prices Singapore’s skills like a stock market on real jobs data, shows you
whether your career is appreciating or depreciating against a national baseline, and
turns the answer into one explainable, subsidised course to take next.**