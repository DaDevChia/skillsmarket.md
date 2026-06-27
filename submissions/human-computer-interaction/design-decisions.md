# SkillsMarket HCI Design Decisions

## 1. Shift from dashboard-first to user-first

Initial versions exposed the market board immediately. User feedback showed that visitors did not know what action to take first. The product now prioritizes resume upload, paste, example profile selection, and manual skill entry.

## 2. Multi-page structure

The application is split into focused pages to reduce compression:

| Route | Purpose |
|---|---|
| `/` | Executive market overview and entry points |
| `/resume` | Resume upload, paste, examples, manual skills, AI analysis workbench |
| `/skills` | Full searchable/sortable skills market board |
| `/skills/:skill` | Skill quote page with valuation, methodology, sources, history |
| `/methodology` | Pricing/rating methodology |
| `/sources` | Source and data-pipeline explanation |

## 3. Bloomberg-terminal aesthetic, not generic AI SaaS

The user explicitly preferred a dense, dark, market-analysis feel. The UI direction uses:

- Tickers
- Quote cards
- Skill symbols
- Sparklines/history charts
- Analyst notes
- Confidence/source chips
- Terminal typography
- High-contrast market colours

The design must remain readable, especially on mobile. Terminal cruelty is not a feature.

## 4. Evidence-grounded AI analysis

Resume analysis must not be a black-box score. The workbench highlights the document spans used as evidence and ties them to skills, roles, achievements, and recommendations.

Design principle:

> Every recommendation should trace back to either document evidence, market data, or a clearly labelled seeded assumption.

## 5. Source honesty

The product distinguishes:

- **MyCareersFuture**: underlying job posting source when used.
- **Apify**: ingestion/scraping/automation infrastructure, not the original data owner.
- **SkillsFuture/MySkillsFuture**: course/training recommendation source.
- **LinkedIn**: only shown as integrated if actually ingested; otherwise labelled not currently ingested or planned.
- **Seeded data**: clearly labelled as fixture/proxy/demo data.

## 6. Skill rating methodology must be explainable

Each skill rating should expose:

- Demand score
- Supply/applicant proxy
- Salary/job-money proxy where present
- Support count
- Provenance
- Seeded vs live status
- Frozen divisor
- Baseline 100 meaning
- Confidence and limitations

## 7. Historical valuation

The user requested historical skill valuation. If real snapshot history exists, use it. Otherwise deterministic seeded history is acceptable only when labelled clearly as a seeded historical proxy.

## 8. Actionable recommendations

Recommendations should include:

- Skill to learn next
- Why it matters against the user's evidence and market index
- How to prove the skill in a resume/project
- Suggested role direction
- SkillsFuture/MySkillsFuture course links or course matches where feasible
