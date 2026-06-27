from skillsmarket.fixtures import COURSES


def test_course_rows_include_required_provenance_fields():
    required = {"title", "provider", "mapped_skill", "duration", "cost_label", "enrolment_url", "provenance"}
    assert COURSES
    for course in COURSES:
        assert required <= set(course)
