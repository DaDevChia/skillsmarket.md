from skillsmarket.llm import build_grounded_explanation_prompt


def test_build_grounded_explanation_prompt_requires_structured_facts():
    try:
        build_grounded_explanation_prompt({})
    except ValueError as exc:
        assert "structured" in str(exc).lower()
    else:
        raise AssertionError("missing structured facts should fail closed")


def test_build_grounded_explanation_prompt_includes_no_hallucination_instruction():
    prompt = build_grounded_explanation_prompt(
        {
            "skill": "Python",
            "price": 142.0,
            "weighted_demand": 74,
            "supply_proxy": 53,
            "divisor": 0.01,
            "source_rows": 12,
            "provenance": "real_proxy",
        }
    )

    assert "Do not invent" in prompt
    assert "Python" in prompt
    assert "142" in prompt
