from skillsmarket.resume import merge_llm_skills_with_deterministic


def test_llm_resume_merge_does_not_add_unknown_skills():
    deterministic = ["Microsoft Excel"]
    llm = ["Microsoft Excel", "Dragon Taming"]

    merged = merge_llm_skills_with_deterministic(
        deterministic, llm, allowed_skills={"Microsoft Excel", "Python"}
    )

    assert merged == ["Microsoft Excel"]


def test_llm_resume_merge_adds_allowed_new_skills_in_order():
    deterministic = ["Microsoft Excel"]
    llm = ["Python", "Microsoft Excel", "Astrology"]

    merged = merge_llm_skills_with_deterministic(
        deterministic, llm, allowed_skills={"Microsoft Excel", "Python"}
    )

    assert merged == ["Microsoft Excel", "Python"]
