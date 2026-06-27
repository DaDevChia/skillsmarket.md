from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


def demo_postings() -> list[dict]:
    """Deterministic MyCareersFuture-shaped internal fixture for demos and tests."""

    return deepcopy(
        [
            {
                "id": "mcf-demo-001",
                "title": "Operations Data Analyst",
                "applications": 32,
                "sector": "Tech",
                "salary_min": 4200,
                "salary_max": 6800,
                "posted_at": "2026-06-01",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "data-analysis", "name": "Data Analysis", "is_key": True},
                    {"id": "python", "name": "Python", "is_key": True},
                    {"id": "data-storytelling", "name": "Data Storytelling", "is_key": True},
                ],
            },
            {
                "id": "mcf-demo-002",
                "title": "AI Operations Associate",
                "applications": 28,
                "sector": "Tech",
                "salary_min": 3900,
                "salary_max": 6200,
                "posted_at": "2026-06-02",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "ai-ops", "name": "AI-Assisted Operations", "is_key": True},
                    {"id": "workflow-automation", "name": "Workflow Automation", "is_key": True},
                    {"id": "data-analysis", "name": "Data Analysis", "is_key": True},
                ],
            },
            {
                "id": "mcf-demo-003",
                "title": "Business Intelligence Coordinator",
                "applications": 44,
                "sector": "Admin",
                "salary_min": 3600,
                "salary_max": 5600,
                "posted_at": "2026-06-03",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "data-storytelling", "name": "Data Storytelling", "is_key": True},
                    {"id": "microsoft-excel", "name": "Microsoft Excel", "is_key": True},
                    {"id": "communication", "name": "Communication", "is_key": False},
                ],
            },
            {
                "id": "mcf-demo-004",
                "title": "Administrative Executive",
                "applications": 155,
                "sector": "Admin",
                "salary_min": 2600,
                "salary_max": 3900,
                "posted_at": "2026-06-04",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "administration", "name": "Administration", "is_key": True},
                    {"id": "microsoft-excel", "name": "Microsoft Excel", "is_key": True},
                    {"id": "scheduling", "name": "Scheduling", "is_key": True},
                    {"id": "team-player", "name": "Team Player", "is_key": False},
                ],
            },
            {
                "id": "mcf-demo-005",
                "title": "Office Administrator",
                "applications": 140,
                "sector": "Admin",
                "salary_min": 2500,
                "salary_max": 3600,
                "posted_at": "2026-06-05",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "administration", "name": "Administration", "is_key": True},
                    {"id": "customer-service", "name": "Customer Service", "is_key": True},
                    {"id": "communication", "name": "Communication", "is_key": False},
                ],
            },
            {
                "id": "mcf-demo-006",
                "title": "Sustainability Reporting Analyst",
                "applications": 35,
                "sector": "Green",
                "salary_min": 4300,
                "salary_max": 7200,
                "posted_at": "2026-06-06",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "sustainability-reporting", "name": "Sustainability Reporting", "is_key": True},
                    {"id": "data-analysis", "name": "Data Analysis", "is_key": True},
                    {"id": "data-storytelling", "name": "Data Storytelling", "is_key": True},
                ],
            },
            {
                "id": "mcf-demo-007",
                "title": "Process Automation Specialist",
                "applications": 30,
                "sector": "Tech",
                "salary_min": 4800,
                "salary_max": 7600,
                "posted_at": "2026-06-07",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "ai-ops", "name": "AI-Assisted Operations", "is_key": True},
                    {"id": "workflow-automation", "name": "Workflow Automation", "is_key": True},
                    {"id": "python", "name": "Python", "is_key": True},
                ],
            },
            {
                "id": "mcf-demo-008",
                "title": "Executive Assistant",
                "applications": 165,
                "sector": "Admin",
                "salary_min": 2800,
                "salary_max": 4200,
                "posted_at": "2026-06-08",
                "source": "MyCareersFuture fixture",
                "skills": [
                    {"id": "administration", "name": "Administration", "is_key": True},
                    {"id": "microsoft-excel", "name": "Microsoft Excel", "is_key": True},
                    {"id": "communication", "name": "Communication", "is_key": False},
                    {"id": "team-player", "name": "Team Player", "is_key": False},
                ],
            },
        ]
    )


PERSONAS = {
    "mdm-lim": {
        "id": "mdm-lim",
        "name": "Mdm Lim",
        "age": 47,
        "current_role": "Retrenched admin executive",
        "target_role": "Data-enabled operations coordinator",
        "holdings": [
            "Microsoft Excel",
            "Administration",
            "Scheduling",
            "Customer Service",
            "Communication",
        ],
        "target_skills": [
            "Data Analysis",
            "Data Storytelling",
            "Workflow Automation",
            "AI-Assisted Operations",
        ],
        "story": "Mdm Lim has strong admin experience but needs one concrete bridge skill into data-enabled operations.",
    }
}

COURSES = [
    {
        "id": "course-data-storytelling",
        "title": "Data Storytelling for Business Operations",
        "provider": "SkillsFuture demo provider",
        "mapped_skill": "Data Storytelling",
        "duration": "6 weeks",
        "cost_label": "~S$180 after subsidy, demo-curated",
        "enrolment_url": "https://www.myskillsfuture.gov.sg/content/portal/en/index.html",
        "provenance": "curated_demo",
    },
    {
        "id": "course-data-analysis",
        "title": "Applied Data Analysis with Spreadsheets and Python",
        "provider": "SkillsFuture demo provider",
        "mapped_skill": "Data Analysis",
        "duration": "8 weeks",
        "cost_label": "~S$240 after subsidy, demo-curated",
        "enrolment_url": "https://www.myskillsfuture.gov.sg/content/portal/en/index.html",
        "provenance": "curated_demo",
    },
    {
        "id": "course-ai-ops",
        "title": "AI-Assisted Operations and Workflow Automation",
        "provider": "SkillsFuture demo provider",
        "mapped_skill": "AI-Assisted Operations",
        "duration": "5 weeks",
        "cost_label": "~S$210 after subsidy, demo-curated",
        "enrolment_url": "https://www.myskillsfuture.gov.sg/content/portal/en/index.html",
        "provenance": "curated_demo",
    },
]


def active_snapshot() -> dict:
    return {
        "id": "fixture-base-2026-06-24",
        "kind": "fixture",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": "Deterministic demo fixture shaped after MyCareersFuture records.",
        "record_count": len(demo_postings()),
    }
