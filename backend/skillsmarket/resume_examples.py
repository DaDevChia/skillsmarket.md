from __future__ import annotations

from skillsmarket.resume import ResumeExample

# Short, realistic, fixture-safe profiles. No real people; provenance is seeded.
RESUME_EXAMPLES = [
    ResumeExample(
        id="admin-to-data",
        label="Admin executive",
        role="Admin Executive",
        text=(
            "Lim Mei Fern is an administrative executive with 15 years of experience in scheduling, "
            "procurement coordination, Microsoft Excel reporting, customer service, and vendor follow-up. "
            "She prepares weekly operations reports, tracks invoices, coordinates meetings, and maintains "
            "shared spreadsheets for department heads. She has basic dashboard exposure and wants to move "
            "into data-enabled operations coordination."
        ),
    ),
    ResumeExample(
        id="fresh-grad-analytics",
        label="Fresh graduate",
        role="Business Analytics Graduate",
        text=(
            "Recent business analytics graduate with coursework in Python, SQL, statistics, dashboarding, "
            "data visualisation, and market research. Completed capstone projects on customer segmentation "
            "and sales forecasting. Comfortable presenting findings to non-technical stakeholders."
        ),
    ),
    ResumeExample(
        id="logistics-coordinator",
        label="Logistics coordinator",
        role="Logistics Coordinator",
        text=(
            "Logistics coordinator handling shipment scheduling, inventory checks, vendor coordination, "
            "customer updates, route planning, Excel trackers, and exception reporting. Interested in "
            "workflow automation and operations analytics."
        ),
    ),
    ResumeExample(
        id="software-ai-ops",
        label="Software engineer",
        role="Software Engineer",
        text=(
            "Software engineer with experience in Python, API development, cloud deployment, monitoring, "
            "incident response, data pipelines, and internal tooling. Exploring AI-assisted operations, "
            "workflow automation, and MLOps support roles."
        ),
    ),
]
