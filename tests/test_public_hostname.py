from skillsmarket.settings import settings


def test_public_hostname_defaults_to_render_domain():
    assert settings.public_hostname == "skillsmarket.onrender.com"
