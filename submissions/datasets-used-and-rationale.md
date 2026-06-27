# Datasets used and rationale

We wanted SkillsMarket to be based on **real Singapore career data**, not generic career advice. Every
number in the app carries a source badge and a fetch date, and seeded demo data is always labelled.

## MyCareersFuture job postings — the underlying source

Source: https://www.mycareersfuture.gov.sg/ — live search API:

```text
POST https://api.mycareersfuture.gov.sg/v2/search
```

**Why and how we use it:** This is the main job-market source. We run a live sweep across ~20 role
queries and pull real postings (≈1,160 jobs), with their listed skills, salary ranges, sectors, and job
links. From this we get real demand (how often a skill appears) and real salary. Because the public API
returns almost no applicant counts, the **live index is priced on real median salary** (the reliable
job-money signal) rather than a sparse supply proxy — and we say so plainly in the methodology. Every live
skill links back to the real job posts behind it.

## MySkillsFuture Course Directory — the course source

Source: https://data.gov.sg/datasets/d_b5802b76f409764c16dde4bf2feb19cd/view

**Why and how we use it:** We ingest the official course directory (~25,800 real courses) via the
data.gov.sg download API and match real courses — title, provider, fee, hours, and a real course-detail
link — to each skill. The goal isn't just "you need data analysis"; it's "here are real courses you can
take next." These are directory matches, not personalised enrolment outcomes.

## Apify — the ingestion / collection layer

Source: https://apify.com/jungle_synthesizer/mycareersfuture-jobs-scraper

**Why and how we use it:** Apify is the scraping/automation infrastructure for secondary validation across
private boards. We treat it as the **tool that collects** data, never as the original source, and it never
sets a price. The integration is built and tested; a comprehensive multi-board sweep needs a paid plan.

## SkillsFuture Jobs-Skills Portal / Skills Frameworks — vocabulary

Source: https://jobsandskills.skillsfuture.gov.sg/frameworks/skills-frameworks

**Why we use it:** To keep messy job-market skill names close to the official Singapore skills and sector
language that SkillsFuture and employers use.

## Seeded demo data — stable, clearly labelled

Repo: https://github.com/DaDevChia/skillsmarket.md

**Why we use it:** A deterministic fixture plus a ~124-skill catalogue keeps the app stable and fast during
judging and powers the demo example profiles. Historical charts are deterministic **seeded backtests** (not
real day-by-day history). All of this is labelled `seeded` / `proxy` in the UI and never presented as live
labour-market truth.

## What we deliberately do not use

**LinkedIn is not ingested.** We list it on the Sources page only to say so explicitly — no LinkedIn data
feeds any price, demand, or salary signal.
