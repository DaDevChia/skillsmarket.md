from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


@dataclass(frozen=True)
class Settings:
    public_hostname: str = os.getenv("SKILLSMARKET_PUBLIC_HOSTNAME", "skillsmarket.onrender.com")
    backend_url: str = os.getenv("SKILLSMARKET_BACKEND_URL", "http://127.0.0.1:8000")
    frontend_url: str = os.getenv("SKILLSMARKET_FRONTEND_URL", "http://127.0.0.1:5173")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-5.4-mini")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    apify_token: str = os.getenv("APIFY_TOKEN", "")
    apify_user_id: str = os.getenv("APIFY_USER_ID", "")
    use_direct_mycareersfuture: bool = os.getenv("USE_DIRECT_MYCAREERSFUTURE", "true").lower() == "true"
    use_apify_secondary: bool = os.getenv("USE_APIFY_SECONDARY", "true").lower() == "true"
    # LLM resume analysis augments (never replaces) the deterministic, text-grounded
    # engine: it runs automatically whenever OPENROUTER_API_KEY is present, and fails
    # closed to the deterministic result on any error. On by default; set
    # SKILLSMARKET_ENABLE_LLM_RESUME=false to force the deterministic-only path even
    # when a key is configured.
    enable_llm_resume: bool = os.getenv("SKILLSMARKET_ENABLE_LLM_RESUME", "true").lower() == "true"
    # Price the market from the latest live MyCareersFuture snapshot (real_proxy)
    # when available. Off by default so tests/personas stay deterministic; on in
    # production via the systemd unit.
    use_live_snapshot: bool = os.getenv("SKILLSMARKET_USE_LIVE_SNAPSHOT", "false").lower() == "true"
    # Auto-research unknown skills with the LLM (uses OPENROUTER key, per-call cost).
    enable_skill_research: bool = os.getenv("SKILLSMARKET_ENABLE_SKILL_RESEARCH", "false").lower() == "true"


settings = Settings()
