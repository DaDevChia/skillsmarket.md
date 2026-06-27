from skillsmarket.apify_sources import APIFY_SECONDARY_ACTORS, actor_for_source


def test_apify_secondary_actor_mapping_excludes_authoritative_price_feed():
    assert actor_for_source("jobstreet") == "memo23/jobstreet-scraper"
    assert actor_for_source("indeed") == "valig/indeed-jobs-scraper"
    assert actor_for_source("google-jobs") == "orgupdate/google-jobs-scraper"
    assert "jungle_synthesizer/mycareersfuture-jobs-scraper" not in APIFY_SECONDARY_ACTORS.values()
