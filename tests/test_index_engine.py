from skillsmarket.engine import compute_market


def test_compute_market_normalizes_median_skill_to_100():
    postings = [
        {
            "id": "job-1",
            "applications": 10,
            "sector": "Admin",
            "skills": [
                {"name": "Python", "is_key": True},
                {"name": "Microsoft Excel", "is_key": False},
            ],
        },
        {
            "id": "job-2",
            "applications": 20,
            "sector": "Tech",
            "skills": [
                {"name": "Python", "is_key": True},
                {"name": "Data Analysis", "is_key": True},
            ],
        },
        {
            "id": "job-3",
            "applications": 40,
            "sector": "Admin",
            "skills": [
                {"name": "Microsoft Excel", "is_key": True},
            ],
        },
    ]

    market = compute_market(postings, min_support=1)

    prices = {skill["name"]: skill["price"] for skill in market["skills"]}
    assert prices["Python"] == 200.0
    assert prices["Microsoft Excel"] == 100.0
    assert prices["Data Analysis"] == 75.0
    assert market["baseline"] == 100.0


def test_compute_market_returns_demand_weighted_sector_indices():
    postings = [
        {
            "id": "job-1",
            "applications": 10,
            "sector": "Admin",
            "skills": [
                {"name": "Microsoft Excel", "is_key": True},
            ],
        },
        {
            "id": "job-2",
            "applications": 20,
            "sector": "Tech",
            "skills": [
                {"name": "Python", "is_key": True},
                {"name": "Data Analysis", "is_key": True},
            ],
        },
    ]

    market = compute_market(postings, min_support=1)

    sectors = {sector["name"]: sector["index"] for sector in market["sectors"]}
    assert sectors["Admin"] == 200.0
    assert sectors["Tech"] == 100.0
