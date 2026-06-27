from skillsmarket.settings import Settings


def test_settings_defaults_are_demo_safe():
    s = Settings()
    assert s.use_direct_mycareersfuture is True
    assert s.use_apify_secondary is True
    assert s.openrouter_model == "openai/gpt-5.4-mini"
