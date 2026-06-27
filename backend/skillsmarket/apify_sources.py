APIFY_SECONDARY_ACTORS = {
    "jobstreet": "memo23/jobstreet-scraper",
    "indeed": "valig/indeed-jobs-scraper",
    "google-jobs": "orgupdate/google-jobs-scraper",
    "all-jobs": "agentx/all-jobs-scraper",
}

APIFY_FALLBACK_ACTORS = {
    "mycareersfuture": "jungle_synthesizer/mycareersfuture-jobs-scraper",
}


def actor_for_source(source: str) -> str:
    key = source.strip().lower()
    if key in APIFY_SECONDARY_ACTORS:
        return APIFY_SECONDARY_ACTORS[key]
    if key in APIFY_FALLBACK_ACTORS:
        return APIFY_FALLBACK_ACTORS[key]
    raise KeyError(f"Unknown Apify source: {source}")
