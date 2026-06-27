"""Seeded skill catalogue that expands the market beyond the core fixture.

The core 12 skills are priced by the pricing engine from the seeded
MyCareersFuture-shaped postings. To make the universe realistic (~100 skills
across Singapore-relevant domains) without pretending we ingested live data,
this module adds authored *seeded* index values on the same 100 = median scale.

Every catalogue skill is labelled provenance="seeded" and carries internally
consistent demand/supply/divisor fields so the explain endpoint still holds
price = (weighted_demand / supply_proxy) / divisor.
"""

from __future__ import annotations

from typing import Any

from skillsmarket.engine import _seeded_change, _skill_id, _symbol_for

# (name, sector, tier). Tier sets the index band; price is spread deterministically
# inside the band by name checksum so the list stays stable and varied.
CATALOG: list[tuple[str, str, str]] = [
    # Admin
    ("Office Administration", "Admin", "common"),
    ("Minute Taking", "Admin", "common"),
    ("Records Management", "Admin", "common"),
    ("Calendar Management", "Admin", "common"),
    ("Data Entry", "Admin", "common"),
    ("Document Control", "Admin", "mid"),
    ("Travel Coordination", "Admin", "common"),
    # Logistics
    ("Supply Chain Coordination", "Logistics", "mid"),
    ("Inventory Management", "Logistics", "mid"),
    ("Warehouse Operations", "Logistics", "common"),
    ("Freight Forwarding", "Logistics", "mid"),
    ("Route Optimisation", "Logistics", "high"),
    ("Customs Documentation", "Logistics", "mid"),
    ("Demand Planning", "Logistics", "high"),
    ("Last-Mile Delivery", "Logistics", "common"),
    # Operations
    ("Process Improvement", "Operations", "mid"),
    ("Lean Six Sigma", "Operations", "high"),
    ("Standard Operating Procedures", "Operations", "common"),
    ("Quality Assurance", "Operations", "mid"),
    ("Vendor Management", "Operations", "mid"),
    ("Capacity Planning", "Operations", "high"),
    ("Operations Analytics", "Operations", "high"),
    # Finance
    ("Financial Analysis", "Finance", "high"),
    ("Accounts Payable", "Finance", "common"),
    ("Accounts Receivable", "Finance", "common"),
    ("Budgeting & Forecasting", "Finance", "mid"),
    ("Management Reporting", "Finance", "mid"),
    ("Financial Modelling", "Finance", "high"),
    ("Audit & Compliance", "Finance", "high"),
    ("Treasury Management", "Finance", "high"),
    ("Cost Accounting", "Finance", "mid"),
    # HR
    ("Recruitment", "HR", "mid"),
    ("Talent Acquisition", "HR", "mid"),
    ("Payroll Administration", "HR", "common"),
    ("Employee Relations", "HR", "mid"),
    ("HR Analytics", "HR", "high"),
    ("Learning & Development", "HR", "mid"),
    ("Compensation & Benefits", "HR", "high"),
    ("HRIS Administration", "HR", "mid"),
    # Sales & Marketing
    ("Digital Marketing", "Sales & Marketing", "mid"),
    ("Search Engine Optimisation", "Sales & Marketing", "mid"),
    ("Content Marketing", "Sales & Marketing", "common"),
    ("Social Media Marketing", "Sales & Marketing", "common"),
    ("CRM Management", "Sales & Marketing", "mid"),
    ("Sales Pipeline Management", "Sales & Marketing", "mid"),
    ("Marketing Analytics", "Sales & Marketing", "high"),
    ("Brand Management", "Sales & Marketing", "high"),
    ("Account Management", "Sales & Marketing", "mid"),
    ("Lead Generation", "Sales & Marketing", "common"),
    # Data & AI
    ("SQL", "Data & AI", "high"),
    ("Machine Learning", "Data & AI", "scarce"),
    ("Data Engineering", "Data & AI", "scarce"),
    ("Power BI", "Data & AI", "high"),
    ("Tableau", "Data & AI", "high"),
    ("Natural Language Processing", "Data & AI", "scarce"),
    ("Computer Vision", "Data & AI", "scarce"),
    ("Deep Learning", "Data & AI", "scarce"),
    ("MLOps Engineering", "Data & AI", "scarce"),
    ("Generative AI", "Data & AI", "scarce"),
    ("Prompt Engineering", "Data & AI", "high"),
    ("Data Governance", "Data & AI", "high"),
    ("ETL Pipelines", "Data & AI", "high"),
    ("Big Data (Spark)", "Data & AI", "scarce"),
    # Software
    ("JavaScript", "Software", "high"),
    ("TypeScript", "Software", "high"),
    ("React", "Software", "high"),
    ("Node.js", "Software", "high"),
    ("Java", "Software", "mid"),
    ("Golang", "Software", "scarce"),
    ("REST API Development", "Software", "high"),
    ("Microservices", "Software", "scarce"),
    ("Software Testing", "Software", "mid"),
    ("Version Control (Git)", "Software", "mid"),
    ("Mobile Development", "Software", "high"),
    ("System Design", "Software", "scarce"),
    # Cybersecurity
    ("Network Security", "Cybersecurity", "high"),
    ("Penetration Testing", "Cybersecurity", "scarce"),
    ("Security Operations (SOC)", "Cybersecurity", "high"),
    ("Identity & Access Management", "Cybersecurity", "high"),
    ("Threat Intelligence", "Cybersecurity", "scarce"),
    ("Application Security", "Cybersecurity", "scarce"),
    ("Security Compliance (GRC)", "Cybersecurity", "high"),
    # Cloud
    ("Amazon Web Services", "Cloud", "scarce"),
    ("Microsoft Azure", "Cloud", "high"),
    ("Google Cloud Platform", "Cloud", "high"),
    ("Kubernetes", "Cloud", "scarce"),
    ("Docker", "Cloud", "high"),
    ("Terraform", "Cloud", "scarce"),
    ("CI/CD Pipelines", "Cloud", "high"),
    ("Site Reliability Engineering", "Cloud", "scarce"),
    ("Cloud Security", "Cloud", "scarce"),
    # Healthcare Admin
    ("Patient Scheduling", "Healthcare Admin", "common"),
    ("Medical Records Management", "Healthcare Admin", "common"),
    ("Claims Processing", "Healthcare Admin", "mid"),
    ("Clinic Operations", "Healthcare Admin", "mid"),
    ("Health Informatics", "Healthcare Admin", "high"),
    # Education & Training
    ("Curriculum Development", "Education", "mid"),
    ("Instructional Design", "Education", "high"),
    ("Classroom Facilitation", "Education", "common"),
    ("E-Learning Development", "Education", "mid"),
    ("Training Needs Analysis", "Education", "mid"),
    # Manufacturing
    ("Production Planning", "Manufacturing", "mid"),
    ("CNC Machining", "Manufacturing", "mid"),
    ("Quality Control", "Manufacturing", "common"),
    ("Maintenance Engineering", "Manufacturing", "mid"),
    ("Industrial Automation", "Manufacturing", "high"),
    ("Robotics", "Manufacturing", "scarce"),
    ("Workplace Safety (WSH)", "Manufacturing", "mid"),
    # Sustainability
    ("ESG Reporting", "Sustainability", "high"),
    ("Carbon Accounting", "Sustainability", "high"),
    ("Sustainability Strategy", "Sustainability", "high"),
    ("Energy Management", "Sustainability", "mid"),
    ("Circular Economy", "Sustainability", "mid"),
    # Project Management
    ("Project Coordination", "Project Management", "mid"),
    ("Agile & Scrum", "Project Management", "high"),
    ("Stakeholder Management", "Project Management", "mid"),
    ("Risk Management", "Project Management", "high"),
    ("Programme Management", "Project Management", "high"),
    ("Project Budget Management", "Project Management", "mid"),
    # Communication
    ("Technical Writing", "Communication", "mid"),
    ("Public Speaking", "Communication", "common"),
    ("Negotiation", "Communication", "mid"),
    ("Cross-Cultural Communication", "Communication", "common"),
    ("Copywriting", "Communication", "common"),
]

TIER_BANDS: dict[str, tuple[int, int]] = {
    "scarce": (158, 236),
    "high": (110, 157),
    "mid": (84, 109),
    "common": (44, 83),
}


def _checksum(name: str) -> int:
    return sum(ord(char) for char in name)


def catalog_price(name: str, tier: str) -> float:
    low, high = TIER_BANDS[tier]
    span = high - low
    checksum = _checksum(name)
    return round(low + (checksum * 7) % span + (checksum % 100) / 100.0, 2)


def build_catalog_skills(divisor: float) -> list[dict[str, Any]]:
    """Build full, engine-shaped seeded skill rows on the given divisor scale."""
    divisor = divisor or 1.0
    skills: list[dict[str, Any]] = []
    for name, sector, tier in CATALOG:
        price = catalog_price(name, tier)
        checksum = _checksum(name)
        supply = round(8 + (checksum % 60) + (checksum % 10) / 10.0, 2)
        raw = price * divisor
        weighted_demand = round(raw * supply, 4)
        source_rows = 3 + (checksum % 10)
        skills.append(
            {
                "id": _skill_id(name),
                "symbol": _symbol_for(name),
                "name": name,
                "sector": sector,
                "sectors": [{"name": sector, "weight": 1.0}],
                "price": price,
                "change": _seeded_change(name, price),
                "demand": weighted_demand,
                "weighted_demand": weighted_demand,
                "supply": supply,
                "supply_proxy": supply,
                "raw_score": round(raw, 6),
                "source_rows": [f"seed-{name[:3].lower()}-{i}" for i in range(source_rows)],
                "source_row_count": source_rows,
                "salary_mid": None,
                "salary_premium": None,
                "is_soft_skill": False,
                "provenance": "seeded",
                "unit": "points",
            }
        )
    return skills


def augment_market_with_catalog(market: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the market with catalogue skills merged in by price.

    Baseline and divisor are preserved; catalogue rows that duplicate an
    engine-priced core skill are skipped so the core stays authoritative.
    """
    existing = {str(skill["name"]).lower() for skill in market.get("skills", [])}
    extra = [skill for skill in build_catalog_skills(market.get("divisor", 1.0)) if skill["name"].lower() not in existing]
    augmented = dict(market)
    augmented["skills"] = sorted([*market.get("skills", []), *extra], key=lambda skill: skill["price"], reverse=True)
    return augmented


def catalog_skill_names() -> list[str]:
    return [name for name, _sector, _tier in CATALOG]
