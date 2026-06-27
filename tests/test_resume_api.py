from fastapi.testclient import TestClient

from skillsmarket.api import app

client = TestClient(app)


def test_resume_examples_endpoint_returns_examples():
    response = client.get("/api/resume/examples")
    assert response.status_code == 200
    examples = response.json()["examples"]
    assert len(examples) >= 4
    first = examples[0]
    assert {"id", "label", "role"} <= set(first)


def test_analyze_example_returns_indexed_skills():
    response = client.post("/api/resume/analyze-example/admin-to-data")
    assert response.status_code == 200
    body = response.json()
    assert body["personal_index"] > 0
    assert body["skills"]
    assert body["actions"]
    assert body["source"] == "example:admin-to-data"


def test_analyze_unknown_example_returns_404():
    response = client.post("/api/resume/analyze-example/does-not-exist")
    assert response.status_code == 404


def test_analyze_text_returns_concise_methodology():
    response = client.post(
        "/api/resume/analyze-text",
        json={"text": "Python and Microsoft Excel reporting with dashboards"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["methodology_summary"].startswith("100 =")
    assert any(skill["name"] == "Python" for skill in body["skills"])


def test_analyze_text_rejects_too_short_input():
    response = client.post("/api/resume/analyze-text", json={"text": "Python"})
    assert response.status_code == 422


def test_upload_txt_resume_returns_analysis():
    content = b"Admin executive with Microsoft Excel, scheduling, and customer service experience."
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.txt", content, "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "upload:resume.txt"
    assert body["skills"]


def test_upload_unsupported_type_returns_415():
    # PDF/DOCX/TXT are supported; an image is not -> clear 415, not a silent failure.
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.png", b"\x89PNG fake", "image/png")},
    )
    assert response.status_code == 415
