# SkillsMarket Understanding

## Core idea

SkillsMarket is a Singapore-focused career market dashboard: it treats skills like market securities, prices them using real job-market supply and demand signals, then turns the result into a concrete learning recommendation.

The user-facing line is:

> Is your career appreciating or depreciating, and what is the single best subsidised skill/course to learn next?

## Product metaphor

- Individual skills = securities quoted in index points.
- National median skill = 100 baseline.
- Sector indices = demand-weighted baskets of skills.
- Career Index = weighted average of a person's current skills.
- Recommendation = "simulate the trade", meaning acquire a skill/course and see index uplift.

This is not a betting app. It is an employability index with market-style UX.

## MVP spine

1. Ingest/cache MyCareersFuture job postings.
2. Extract skills, key-skill flags, application counts, salaries, categories, dates.
3. Aggregate demand and supply proxy per skill.
4. Compute skill price:

```text
price(skill) = (demand / supply_proxy) / frozen_divisor
```

where the divisor is set so the median skill equals 100.

5. De-noise generic skills:
   - key skills weighted higher,
   - soft-skill stoplist/downweighting,
   - minimum posting support threshold.
6. Build:
   - Big Board ticker,
   - sector indices,
   - personal Career Index,
   - recommendation/trade simulator,
   - shock demo button.

## Hackathon demo persona

Mdm Lim, 47, retrenched admin executive.

Flow:

1. Enter role.
2. Show Career Index below 100.
3. Click a weak/fading skill to explain the quote from data.
4. Recommend one subsidised course.
5. Simulate Career Index uplift.
6. Press GenAI shock button and show market repricing.

## Important product constraints

- Points, not dollars, are the headline unit.
- Salary is only secondary hover/detail signal.
- No gambling language beyond safe financial-market/index metaphors.
- Every recommendation must be explainable from dataset rows.
- Cache data for demo stability; do not rely on live API during the pitch.
- MVP can use curated Skills Framework/course mappings for the persona while preserving the architecture for full mapping later.

## Likely initial build shape

- Backend: Python FastAPI.
- Data engine: pandas or Polars.
- Frontend: Vite/React or simple HTML dashboard, depending on speed.
- Demo data: cached MyCareersFuture snapshot plus seeded course mappings.
- API endpoints:
  - `/api/market/skills`
  - `/api/market/sectors`
  - `/api/persona/{role}`
  - `/api/simulate-trade`
  - `/api/shock/genai`
  - `/api/explain/{skill}`

## First implementation target

Build a convincing local demo before chasing perfect ingestion:

1. Create engine with deterministic fixture data.
2. Build dashboard UI around engine output.
3. Add ingestion path once the display works.
4. Replace fixtures with cached live snapshot.

Judges see the board and explanation first; nobody awards points for a heroic scraper quietly dying in the corner.
