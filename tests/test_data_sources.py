from skillsmarket.data_sources import (
    BASELINE_EXPLAINER,
    DATA_LIMITS,
    DATA_SOURCES,
    PIPELINE_STAGES,
)


def _by_name(name: str) -> dict:
    return next(source for source in DATA_SOURCES if source["name"] == name)


def test_data_sources_mark_authoritative_and_secondary_sources():
    authoritative = [source for source in DATA_SOURCES if source["role"] == "authoritative_price_feed"]
    secondary = [source for source in DATA_SOURCES if source["role"] == "secondary_validation"]

    assert authoritative[0]["name"] == "MyCareersFuture"
    assert authoritative[0]["access"] == "direct_public_api"
    assert any(source["name"] == "JobStreet / JobsDB" for source in secondary)


def test_apify_is_labelled_ingestion_infrastructure_not_a_source():
    apify = _by_name("Apify")
    assert apify["role"] == "ingestion_infrastructure"
    assert apify["kind"] == "ingestion_infrastructure"


def test_skillsfuture_is_the_course_source_directory_ingested():
    skillsfuture = _by_name("SkillsFuture / MySkillsFuture")
    assert skillsfuture["role"] == "course_source"
    assert skillsfuture["status"] == "directory_ingested"
    # Honest: real directory ingested, matched by keyword (not personalised enrolment).
    assert "course directory" in skillsfuture["use"].lower()


def test_baseline_explainer_defines_one_hundred():
    assert BASELINE_EXPLAINER.startswith("100 =")


def test_pipeline_flows_postings_to_courses():
    stages = [stage["id"] for stage in PIPELINE_STAGES]
    assert stages == ["postings", "ingest", "engine", "match", "courses"]
    # Apify stage is ingestion infrastructure, MyCareersFuture is the source.
    by_id = {stage["id"]: stage for stage in PIPELINE_STAGES}
    assert by_id["postings"]["kind"] == "underlying_source"
    assert by_id["ingest"]["kind"] == "ingestion_infrastructure"


def test_limits_mention_seeded_and_proxy():
    blob = " ".join(DATA_LIMITS).lower()
    assert "seeded" in blob
    assert "proxy" in blob
