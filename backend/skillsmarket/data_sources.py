"""Honest data-source, pipeline, and provenance labelling.

Distinctions this module keeps straight (verified against ingest.py /
apify_sources.py / courses.py):
- MyCareersFuture job postings are the *underlying source* of job demand,
  applicant counts (a supply proxy), and salary bands where present.
- Apify is *ingestion/scraping/automation infrastructure* used to collect
  job-market data (titles, skill mentions, applicant/salary fields). It is the
  collection tool, not the original labour-market source, and never sets price.
- SkillsFuture / MySkillsFuture is the *training-course source* for next-step
  recommendations, surfaced as curated course-directory search links (not live
  enrolment results).
"""

from skillsmarket.courses import COURSE_DIRECTORY_DATASET_ID

BASELINE_EXPLAINER = (
    "100 = the median skill price across the current snapshot. "
    "Above 100 = scarcer / higher demand relative to supply. Below 100 = more common."
)

DATA_SOURCES = [
    {
        "name": "MyCareersFuture",
        "role": "authoritative_price_feed",
        "kind": "underlying_source",
        "status": "live_sweep_with_seeded_fallback",
        "label": "Underlying source — live job sweep (real salary, demand) with seeded fallback",
        "access": "direct_public_api",
        "url": "https://api.mycareersfuture.gov.sg/v2/search",
        "use": "Government job-postings API. The underlying source of demand and salary. We run a live "
        "search sweep across domains; in live mode the index is priced on real median salary (applicant "
        "counts are sparse in the API, so salary is the reliable signal). Seeded fixture is the deterministic "
        "fallback. Every live skill links to real job UUIDs.",
    },
    {
        "name": "Apify",
        "role": "ingestion_infrastructure",
        "kind": "ingestion_infrastructure",
        "status": "configured_real_actors",
        "label": "Ingestion / scraping / automation infrastructure — not the original source",
        "access": "apify_actors",
        "use": "Scraping/collection/automation infrastructure used to gather job-market data — job titles, "
        "skill mentions, applicant counts, and salary/job-money fields where present — across boards "
        "(JobStreet/JobsDB, Indeed, Google Jobs). A collection tool, not the labour-market source, and it "
        "never sets the price.",
    },
    {
        "name": "JobStreet / JobsDB",
        "role": "secondary_validation",
        "kind": "underlying_source",
        "status": "configured_real_actor",
        "label": "Secondary validation board (collected via Apify)",
        "access": "apify",
        "actor": "memo23/jobstreet-scraper",
        "use": "Private-market demand triangulation, not official price calculation.",
    },
    {
        "name": "Indeed",
        "role": "secondary_validation",
        "kind": "underlying_source",
        "status": "configured_real_actor",
        "label": "Secondary validation board (collected via Apify)",
        "access": "apify",
        "actor": "valig/indeed-jobs-scraper",
        "use": "Additional broad demand signal, not official price calculation.",
    },
    {
        "name": "Google Jobs",
        "role": "secondary_validation",
        "kind": "underlying_source",
        "status": "configured_real_actor",
        "label": "Secondary validation board (collected via Apify)",
        "access": "apify",
        "actor": "orgupdate/google-jobs-scraper",
        "use": "Aggregated cross-board trend check, not official price calculation.",
    },
    {
        "name": "SkillsFuture / MySkillsFuture",
        "role": "course_source",
        "kind": "course_source",
        "status": "directory_ingested",
        "label": "Training-course source — real Course Directory ingested (data.gov.sg)",
        "access": "course_directory",
        "url": "https://courses.myskillsfuture.gov.sg/search",
        "dataset_id": COURSE_DIRECTORY_DATASET_ID,
        "use": "Official MySkillsFuture Course Directory, ingested from data.gov.sg. Real courses (title, "
        "provider, fee, hours, course-detail link) are matched to each skill. Matches are by title/keyword "
        "against the live directory, not personalised enrolment outcomes.",
    },
    {
        "name": "LinkedIn",
        "role": "not_a_source",
        "kind": "not_ingested",
        "status": "not_currently_ingested",
        "label": "Not currently ingested — planned / optional",
        "access": "none",
        "use": "LinkedIn is NOT ingested in this build. Listed only to be explicit: no LinkedIn data feeds "
        "any price, demand, or salary signal here. It is a possible future / optional source.",
    },
    {
        "name": "data.gov.sg labour datasets",
        "role": "phase_2_structural_calibration",
        "kind": "planned",
        "status": "planned_real",
        "label": "Planned — not yet used",
        "access": "direct_public_api",
        "url": "https://data.gov.sg/api/action/datastore_search?resource_id={dataset_id}",
        "use": "Sector employment, training supply, labour-force calibration. Planned, not yet wired.",
    },
]

# Left-to-right flow shown in the Sources & Data Pipeline panel.
PIPELINE_STAGES = [
    {
        "id": "postings",
        "label": "MyCareersFuture postings",
        "kind": "underlying_source",
        "detail": "Job demand, applicant counts (supply proxy), and salary bands where present.",
    },
    {
        "id": "ingest",
        "label": "Apify ingestion / snapshot",
        "kind": "ingestion_infrastructure",
        "detail": "Scraping/collection/automation for titles, skill mentions, applicant & salary fields. Collection tool, not the source.",
    },
    {
        "id": "engine",
        "label": "SkillsMarket pricing engine",
        "kind": "engine",
        "detail": "Price = weighted demand ÷ supply proxy, normalised so 100 = median. Frozen divisor keeps snapshots comparable.",
    },
    {
        "id": "match",
        "label": "Resume evidence matching",
        "kind": "engine",
        "detail": "Token-grounded skill / role / achievement spans matched to the index — no invented evidence.",
    },
    {
        "id": "courses",
        "label": "SkillsFuture course & action recs",
        "kind": "course_source",
        "detail": "Curated MySkillsFuture course searches and next actions per recommended skill.",
    },
]

DATA_LIMITS = [
    "This public demo runs on a seeded fixture; a live proxy snapshot is used only when one is ingested.",
    "Salary / money fields are used only when present in a posting.",
    "Applicant counts are an imperfect supply proxy, not a true labour-supply count.",
    "Course links are curated MySkillsFuture searches, not live enrolment results.",
    "Catalogue skills carry seeded index values on the same 100 = median scale, labelled seeded.",
]

PROVENANCE_ROWS = [
    {"signal": "Skill demand", "status": "seeded", "source": "Fixture rows shaped after the MyCareersFuture schema"},
    {"signal": "Competition proxy", "status": "seeded", "source": "Fixture applicant counts — imperfect supply proxy"},
    {"signal": "Salary", "status": "seeded", "source": "Fixture salary bands, used only where present"},
    {"signal": "Course mapping", "status": "curated_demo", "source": "Curated MySkillsFuture search links (not live enrolment)"},
    {"signal": "Historical movement", "status": "seeded", "source": "Deterministic demo shock, labelled"},
]
