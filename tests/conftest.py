"""Shared test config.

The resume analyser now calls the LLM automatically whenever an OPENROUTER_API_KEY
is present. To keep the suite deterministic, offline, and free, we disable that
call by default for every test. Tests that exercise the AI path re-stub the
function explicitly (their monkeypatch runs after this fixture and wins).
"""

from __future__ import annotations

import pytest

import skillsmarket.api as api


@pytest.fixture(autouse=True)
def _offline_llm_resume_by_default(monkeypatch):
    monkeypatch.setattr(api, "analyze_resume_with_openrouter", lambda *args, **kwargs: None)
