import io
import pytest
from fastapi.testclient import TestClient
from main import app, extract_text_from_pdf, CVEvaluationReport, InterviewQuestion
import pypdf

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns 200 OK and expected structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "HR CV Analyzer AI"
    assert "groq_configured" in data or "gemini_configured" in data


def test_analyze_invalid_file_extension():
    """Verify POST /api/analyze rejects unsupported file formats."""
    files = {
        "cv_file": ("test.png", b"fake image bytes", "image/png")
    }
    data = {
        "job_description": "Looking for a Python backend developer with FastAPI and PostgreSQL skills."
    }
    response = client.post("/api/analyze", data=data, files=files)
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]


def test_analyze_short_job_description():
    """Verify POST /api/analyze rejects empty or short job descriptions."""
    files = {
        "cv_file": ("resume.pdf", b"dummy pdf content", "application/pdf")
    }
    data = {
        "job_description": "Short"
    }
    response = client.post("/api/analyze", data=data, files=files)
    assert response.status_code == 400
    assert "Job Description is too short" in response.json()["detail"]


def test_pypdf_text_extraction():
    """Verify extract_text_from_pdf function extracts text properly."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    
    pdf_bytes_io = io.BytesIO()
    writer.write(pdf_bytes_io)
    pdf_bytes = pdf_bytes_io.getvalue()
    
    # Should raise error for empty page without text
    with pytest.raises(Exception):
        extract_text_from_pdf(pdf_bytes)


def test_cv_evaluation_schema():
    """Verify Pydantic CVEvaluationReport schema initialization."""
    report = CVEvaluationReport(
        candidate_name="Jane Doe",
        match_score=90,
        recommendation="Strong Fit",
        candidate_summary="Outstanding candidate with 6 years Python experience.",
        matched_skills=["Python", "FastAPI", "Docker"],
        missing_skills=["Kubernetes"],
        red_flags=[],
        interview_questions=[
            InterviewQuestion(
                question="How do you handle database migrations in FastAPI?",
                rationale="Verifies practical PostgreSQL & Alembic skills.",
                expected_answer="Mentions Alembic, version control for DB schemas, and zero-downtime strategy."
            )
        ]
    )
    assert report.match_score == 90
    assert report.candidate_name == "Jane Doe"
    assert len(report.matched_skills) == 3
    assert len(report.interview_questions) == 1
