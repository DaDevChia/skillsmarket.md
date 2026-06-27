FROM node:22-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html tsconfig.json tsconfig.node.json vite.config.ts ./
COPY src ./src
RUN npm run build

FROM python:3.11-slim AS app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend \
    PORT=8000

RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
COPY backend ./backend
COPY scripts ./scripts
COPY --from=frontend /app/dist ./dist
RUN uv sync --frozen --no-dev
RUN PYTHONPATH=backend uv run python scripts/render_prepare_data.py

EXPOSE 8000
CMD ["sh", "-c", "uv run uvicorn skillsmarket.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
