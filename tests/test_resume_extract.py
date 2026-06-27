import io

import pytest
from fastapi.testclient import TestClient

from skillsmarket.api import app
from skillsmarket.extract import (
    ResumeExtractionError,
    UnsupportedResumeFormat,
    extract_resume_text,
)

client = TestClient(app)


def _make_pdf(text: str) -> bytes:
    """Build a minimal valid single-page PDF whose text pypdf can extract."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        None,  # content stream, filled below
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    stream = b"BT /F1 18 Tf 72 700 Td (" + text.encode("latin-1") + b") Tj ET"
    objects[3] = b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"

    pdf = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n"
    xref_pos = len(pdf)
    pdf += b"xref\n0 " + str(len(objects) + 1).encode() + b"\n0000000000 65535 f \n"
    for off in offsets:
        pdf += ("%010d 00000 n \n" % off).encode()
    pdf += b"trailer\n<< /Size " + str(len(objects) + 1).encode() + b" /Root 1 0 R >>\n"
    pdf += b"startxref\n" + str(xref_pos).encode() + b"\n%%EOF"
    return pdf


def _make_docx(text: str) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_extract_txt():
    out = extract_resume_text("resume.txt", b"Python and Microsoft Excel reporting")
    assert "Python" in out


def test_extract_pdf():
    out = extract_resume_text("resume.pdf", _make_pdf("Python Microsoft Excel Data Analysis"))
    assert "Python" in out
    assert "Excel" in out


def test_extract_docx():
    out = extract_resume_text("resume.docx", _make_docx("Python and Microsoft Excel and Data Analysis"))
    assert "Microsoft Excel" in out


def test_extract_unsupported_format_raises():
    with pytest.raises(UnsupportedResumeFormat):
        extract_resume_text("resume.rtf", b"some bytes")


def test_extract_corrupt_pdf_raises_extraction_error():
    with pytest.raises(ResumeExtractionError):
        extract_resume_text("resume.pdf", b"not really a pdf at all")


# ---- end-to-end through the upload endpoint ----

def test_upload_pdf_returns_analysis():
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", _make_pdf("Python Microsoft Excel Data Analysis"), "application/pdf")},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "upload:resume.pdf"
    assert any(skill["name"] == "Python" for skill in body["skills"])
    # Highlights must render from the extracted PDF text with valid spans.
    assert body["highlights"]
    doc = body["document_text"]
    for h in body["highlights"]:
        assert doc[h["start"]:h["end"]] == h["text"]


def test_upload_docx_returns_analysis():
    response = client.post(
        "/api/resume/upload",
        files={
            "file": (
                "resume.docx",
                _make_docx("Python and Microsoft Excel and Data Analysis"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "upload:resume.docx"
    assert body["highlights"]
    assert body["document_text"]


def test_upload_unsupported_type_returns_415():
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.png", b"\x89PNG fake", "image/png")},
    )
    assert response.status_code == 415


def test_upload_unreadable_pdf_returns_422():
    response = client.post(
        "/api/resume/upload",
        files={"file": ("resume.pdf", b"%PDF-1.4 broken", "application/pdf")},
    )
    assert response.status_code == 422
