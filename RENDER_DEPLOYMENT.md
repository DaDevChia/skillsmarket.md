# Render deployment

This repo is prepared for a single-service Render deployment.

## Recommended setup

Use one Render **Web Service** from the public GitHub repo:

```text
https://github.com/DaDevChia/skillsmarket.md
```

Render reads:

```text
render.yaml
Dockerfile
```

The Docker build:

1. installs frontend dependencies with `npm ci`,
2. builds the Vite/React app into `dist/`,
3. installs Python dependencies with `uv`,
4. best-effort warms MyCareersFuture and MySkillsFuture caches,
5. starts FastAPI with Uvicorn,
6. serves `/api/*` plus the built frontend from the same process.

## Environment variables

Set these in Render as secrets or env vars:

```text
SKILLSMARKET_USE_LIVE_SNAPSHOT=true
SKILLSMARKET_ENABLE_LLM_RESUME=true
SKILLSMARKET_ENABLE_SKILL_RESEARCH=true
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-5.4-mini
OPENROUTER_API_KEY=<secret>
APIFY_TOKEN=<optional secret>
APIFY_USER_ID=<optional secret>
```

The app still works without `OPENROUTER_API_KEY`, but resume analysis and add-skill research fall back to deterministic mode.

## Manual Render flow

1. Open Render dashboard.
2. Create **New Web Service** or **Blueprint**.
3. Connect this repo:

```text
https://github.com/DaDevChia/skillsmarket.md
```

4. Use the `render.yaml` detected at the repo root.
5. Fill the secret values Render asks for.
6. Deploy.
7. Verify:

```text
/api/health
/resume
/skills
```

## Local verification

```bash
npm run build
PYTHONPATH=backend uv run pytest -q
PYTHONPATH=backend uv run python - <<'PY'
from fastapi.testclient import TestClient
from skillsmarket.api import app
client = TestClient(app)
for path in ['/api/health', '/', '/resume', '/skills/python']:
    print(path, client.get(path).status_code)
PY
```

## Public URL

Use the Render-hosted public URL:

```text
https://skillsmarket.onrender.com
```

The old Cloudflare Tunnel domain is no longer used for public hosting.

## Notes

Render free web services may sleep after inactivity. Open the URL once before demo or judging so it wakes up.
