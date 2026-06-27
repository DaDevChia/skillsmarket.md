from skillsmarket.engine import compute_market
from skillsmarket.fixtures import demo_postings
from skillsmarket.resume import analyze_resume_text
from skillsmarket.resume_examples import RESUME_EXAMPLES

RICH_TEXT = (
    "Lim Wei is a senior operations analyst with 8 years of experience. "
    "Skilled in Microsoft Excel, Python, and data analysis. "
    "Reduced reporting time by 40% and managed a S$1,200 vendor budget. "
    "Holds a Bachelor degree in Business and a PMP certification."
)


def _market():
    return compute_market(demo_postings(), min_support=1)


def test_highlights_have_valid_spans_and_categories():
    analysis = analyze_resume_text(RICH_TEXT, _market(), source="paste")
    assert analysis.document_text == RICH_TEXT
    assert analysis.highlights
    categories = {h.category for h in analysis.highlights}
    # Skills, a role/title, an education signal, and a measurable achievement.
    assert "skill" in categories or "weak" in categories
    assert "role" in categories
    assert "education" in categories
    assert "achievement" in categories
    for h in analysis.highlights:
        # Spans must point at the real text (no hallucinated evidence).
        assert RICH_TEXT[h.start:h.end] == h.text
        assert 0.0 <= h.confidence <= 1.0


def test_highlights_do_not_overlap():
    analysis = analyze_resume_text(RICH_TEXT, _market(), source="paste")
    spans = sorted((h.start, h.end) for h in analysis.highlights)
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        assert e1 <= s2, "highlights must not overlap"


def test_achievement_percentage_is_highlighted():
    analysis = analyze_resume_text(RICH_TEXT, _market(), source="paste")
    achievements = [h.text for h in analysis.highlights if h.category == "achievement"]
    assert any("%" in a for a in achievements)


def test_example_analysis_has_highlights():
    example = RESUME_EXAMPLES[0]
    analysis = analyze_resume_text(example.text, _market(), source=f"example:{example.id}")
    assert analysis.highlights
    assert any(h.category in {"skill", "weak"} for h in analysis.highlights)


def test_actions_are_rich_and_linked():
    analysis = analyze_resume_text(RICH_TEXT, _market(), source="paste")
    assert 3 <= len(analysis.actions) <= 5
    learn = [a for a in analysis.actions if a.type == "learn"]
    assert learn
    for action in learn:
        assert action.course_url and "myskillsfuture.gov.sg" in action.course_url
        assert "not live" in action.course_note.lower()
        assert action.how_to_prove
        assert action.role_direction
    assert any(a.type == "direction" for a in analysis.actions)


def test_weak_skill_highlight_links_to_an_action():
    analysis = analyze_resume_text(RICH_TEXT, _market(), source="paste")
    weak = [h for h in analysis.highlights if h.category == "weak"]
    # Microsoft Excel is below baseline in the seeded market -> a weak highlight.
    assert weak
    assert any(h.affects for h in weak)
