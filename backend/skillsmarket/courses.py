"""SkillsFuture / MySkillsFuture course linking.

We build *curated search links* into the official MySkillsFuture course
directory. We do NOT claim these are live enrolment results. A live ingestion
path against the data.gov.sg Course Directory dataset is documented below but
not called on the request path (it is heavy and network-bound); the UI is
honest about this.
"""

from __future__ import annotations

from urllib.parse import quote

MYSKILLSFUTURE_SEARCH = "https://courses.myskillsfuture.gov.sg/search"

# Official MySkillsFuture Course Directory on data.gov.sg (for optional live ingest).
COURSE_DIRECTORY_DATASET_ID = "d_b5802b76f409764c16dde4bf2feb19cd"
COURSE_DIRECTORY_POLL_URL = (
    f"https://api-open.data.gov.sg/v1/public/api/datasets/{COURSE_DIRECTORY_DATASET_ID}/poll-download"
)

COURSE_NOTE = "Curated MySkillsFuture course search — not live enrolment results."


def course_search_url(skill: str) -> str:
    """Curated deep-link into the live MySkillsFuture course directory search.

    Uses the directory's current public search params (``q`` + ``termOrigin``) so
    the link lands on real, live results — not a stale data.gov.sg directory page.
    """
    return f"{MYSKILLSFUTURE_SEARCH}?q={quote(skill)}&termOrigin=ORGANIC"
