from skillsmarket.engine import compute_market
from skillsmarket.fixtures import demo_postings
from skillsmarket.resume import (
    ParsedResume,
    ResumeExample,
    analyze_resume_text,
    parse_resume_text,
)
from skillsmarket.resume_examples import RESUME_EXAMPLES


def test_resume_models_are_constructible():
    example = ResumeExample(id="demo", label="Demo", role="Role", text="Some resume text")
    parsed = ParsedResume(skills=["Python"], evidence={"Python": ["Python"]})

    assert example.id == "demo"
    assert parsed.skills == ["Python"]


def test_resume_examples_are_selectable_and_have_text():
    assert len(RESUME_EXAMPLES) >= 4
    for example in RESUME_EXAMPLES:
        assert example.id
        assert example.label
        assert example.role
        assert len(example.text) > 80


def test_parse_resume_text_extracts_known_skills_with_evidence():
    text = "I use Microsoft Excel, Python, workflow automation, and customer service reporting."

    parsed = parse_resume_text(text)

    assert "Microsoft Excel" in parsed.skills
    assert "Python" in parsed.skills
    assert "Workflow Automation" in parsed.skills
    assert parsed.evidence["Python"]


def test_analyze_resume_text_returns_personal_index_and_actions():
    market = compute_market(demo_postings(), min_support=1)
    text = "Admin executive skilled in Microsoft Excel, scheduling, and customer service."

    analysis = analyze_resume_text(text, market, source="paste")

    assert analysis.source == "paste"
    assert analysis.baseline == 100
    assert analysis.personal_index > 0
    assert analysis.skills
    assert analysis.actions
    assert any(skill.name == "Microsoft Excel" for skill in analysis.skills)


def test_analyze_resume_text_separates_strengths_and_gaps():
    market = compute_market(demo_postings(), min_support=1)
    text = (
        "Operations analyst using Python, Data Analysis, Data Storytelling, "
        "Microsoft Excel, scheduling and administration."
    )

    analysis = analyze_resume_text(text, market, source="paste")

    # Strengths sit at or above the 100 baseline; gaps sit below it.
    assert all(skill.price >= analysis.baseline for skill in analysis.strengths)
    assert all(skill.price < analysis.baseline for skill in analysis.gaps)
    assert analysis.strengths or analysis.gaps


def test_analyze_empty_resume_returns_zero_index_and_a_next_step():
    market = compute_market(demo_postings(), min_support=1)

    analysis = analyze_resume_text("I enjoy gardening and long walks.", market, source="paste")

    assert analysis.personal_index == 0
    assert analysis.actions  # should still tell the user what to do next
