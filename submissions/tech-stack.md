# Tech stack

SkillsMarket is a FastAPI + Vite/React app that prices Singapore skills like market instruments. It runs
on **real** MyCareersFuture and SkillsFuture data, with a clearly-labelled seeded fallback so demos stay
stable. The LLM only narrates and researches — it never invents the index.

## Python backend

- **Python 3.11**
- **FastAPI** — backend API: https://fastapi.tiangolo.com/
- **Pydantic** — typed request/response models: https://docs.pydantic.dev/
- **Uvicorn** — ASGI server: https://www.uvicorn.org/
- **httpx** — calls to MyCareersFuture, data.gov.sg, Apify, and OpenRouter: https://www.python-httpx.org/
- **Polars** — data processing for the skill index: https://pola.rs/
- **pypdf** + **python-docx** — resume parsing (PDF / DOCX): https://pypi.org/project/pypdf/ · https://pypi.org/project/python-docx/
- **openpyxl** — reads the MySkillsFuture Course Directory spreadsheet: https://openpyxl.readthedocs.io/
- **python-multipart** — resume file uploads
- **pytest** — backend tests (LLM stubbed offline so the suite is deterministic and free): https://docs.pytest.org/
- **uv** — Python dependency management + reproducible lockfile (`pyproject.toml` / `uv.lock`): https://docs.astral.sh/uv/

## AI / LLM layer

- **OpenRouter** (OpenAI-compatible `/chat/completions`): https://openrouter.ai/
- Model + key come from environment variables, never hardcoded.
- LLM use is limited to three grounded jobs: (1) an **AI resume analyst** readout, (2) **add-skill live
  research**, and (3) plain-English skill explanations.
- **The LLM never invents the index.** Prices are computed from job/course data first. Resume skills are
  intersected with the market vocabulary and every quote is verified verbatim against the resume; new-skill
  research is labelled *AI-researched estimate — not market data*. Every call **fails closed** to the
  deterministic engine.
- Code: [`backend/skillsmarket/llm.py`](../backend/skillsmarket/llm.py) · [`settings.py`](../backend/skillsmarket/settings.py)

## Frontend

- **Vite**: https://vite.dev/ · **React** + **TypeScript**: https://react.dev/
- **three.js** — the 3D skills globe on the resume readout: https://threejs.org/
- Hand-built SVG **interactive stock chart** (pan / zoom / range / crosshair) and sparklines — no chart library.
- **Playwright** — E2E tests across desktop + mobile: https://playwright.dev/

## Data & ingestion

- **MyCareersFuture** job data — the underlying demand/salary source: https://www.mycareersfuture.gov.sg/
  - Live search sweep across domains:
    ```text
    POST https://api.mycareersfuture.gov.sg/v2/search
    ```
- **MySkillsFuture Course Directory** (data.gov.sg, ~25,800 real courses) for course recommendations:
  https://data.gov.sg/datasets/d_b5802b76f409764c16dde4bf2feb19cd/view
- **Apify** — scraping / ingestion infrastructure for secondary validation (collector, not the source):
  https://apify.com/ · MyCareersFuture scraper: https://apify.com/jungle_synthesizer/mycareersfuture-jobs-scraper
- **SkillsFuture Jobs-Skills Portal** — skills/sector vocabulary reference: https://jobsandskills.skillsfuture.gov.sg/
- Real snapshots and per-skill caches are stored under `data/`; everything is labelled `seeded`,
  `real_proxy`, or `ai_researched` so provenance is never ambiguous.

## Deployment & repo

- **Render** for public deployment; FastAPI serves the API and built Vite frontend from one hosted web
  service: https://render.com/
- GitHub repo: https://github.com/DaDevChia/skillsmarket.md
