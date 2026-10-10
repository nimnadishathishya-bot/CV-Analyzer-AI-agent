import os
import io
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import pypdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

app = FastAPI(
    title="HR CV Analyzer AI",
    description="Smart AI CV Screener supporting Google Gemini & Groq APIs",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prevent Browser Stale Caching of Frontend UI
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# --- Data Models ---
class QuestionItem(BaseModel):
    question: str
    rationale: str
    expected_answer: str

InterviewQuestion = QuestionItem


class CVEvaluationReport(BaseModel):
    candidate_name: str = "Candidate"
    match_score: int
    recommendation: str
    candidate_summary: str
    matched_skills: List[str]
    missing_skills: List[str]
    red_flags: List[str]
    interview_questions: List[QuestionItem]


# --- PDF Extractor ---
def extract_text_from_pdf(file_bytes: bytes) -> str:
    # 1. If file does not start with PDF header, check if it's plaintext
    if not file_bytes.startswith(b"%PDF"):
        try:
            decoded = file_bytes.decode('utf-8', errors='ignore').strip()
            if len(decoded) > 20:
                return decoded
        except Exception:
            pass

    # 2. Extract via pypdf with strict=False
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = pypdf.PdfReader(pdf_file, strict=False)
        extracted_text = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)

        full_text = "\n".join(extracted_text).strip()
        if full_text and len(full_text) > 10:
            return full_text
    except Exception as pdf_err:
        # 3. Fallback: If pypdf throws (e.g. Stream ended unexpectedly), attempt text decoding
        try:
            decoded = file_bytes.decode('utf-8', errors='ignore').strip()
            readable = "".join([c for c in decoded if c.isprintable() or c in '\n\r\t']).strip()
            if len(readable) > 30:
                return readable
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF ({str(pdf_err)}). Please ensure your PDF file contains selectable text and is not corrupted."
        )

    # 4. If PDF contains no extractable text
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No readable text found in PDF. The file may contain only scanned images without selectable text."
    )


# --- AI Evaluator (Gemini & Groq Auto-routing) ---
def evaluate_cv_with_ai(cv_text: str, job_description: str) -> CVEvaluationReport:
    load_dotenv(override=True)
    api_key = (
        os.getenv("GEMINI_API_KEY") or 
        os.getenv("GROQ_API_KEY") or 
        os.getenv("API_KEY") or ""
    ).strip().strip("'").strip('"')

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing. Please configure your key in .env file."
        )

    prompt = f"""
You are an expert HR Talent Acquisition Specialist and Technical Recruiter.
Analyze the candidate's CV against the provided Job Description objectively and thoroughly.

### JOB DESCRIPTION:
{job_description}

### CANDIDATE CV:
{cv_text}

Provide an objective evaluation including:
1. Candidate Name (if found in CV, otherwise 'Candidate')
2. Match Score (0 to 100 based strictly on skills, experience, and requirements fit)
3. Recommendation ('Strong Fit', 'Moderate Fit', 'Potential Fit', or 'Not Recommended')
4. Candidate Executive Summary (2-3 detailed paragraphs)
5. Matched Skills (list of skills candidate possesses that match the JD)
6. Missing Skills (list of skills requested in JD that candidate lacks or didn't specify)
7. Red Flags / Concerns (list any gaps, missing experience, or potential concerns)
8. Custom Interview Questions (3-5 items containing 'question', 'rationale', and 'expected_answer')

Return strictly a valid raw JSON object matching the requested schema.
"""

    # If key is Groq (starts with gsk_)
    if api_key.startswith("gsk_"):
        try:
            from groq import Groq
            groq_client = Groq(api_key=api_key)
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            result_json = json.loads(response.choices[0].message.content)
            return CVEvaluationReport(**result_json)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Groq Evaluation error: {str(e)}"
            )

    # Otherwise use Google Gemini API (AQ... / AIza... keys)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Gemini active flash models for API v1beta
        models_to_try = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3-flash-preview']
        response = None
        last_err = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                        response_json_schema=CVEvaluationReport.model_json_schema(),
                        temperature=0.2,
                    ),
                )
                if response and response.text:
                    break
            except Exception as m_err:
                last_err = m_err
                continue

        if not response or not response.text:
            raise ValueError(f"Failed to generate evaluation report: {str(last_err)}")

        report_data = json.loads(response.text)
        return CVEvaluationReport(**report_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gemini API Evaluation error: {str(e)}"
        )


# --- Endpoints ---
@app.get("/api/health")
def health_check():
    """Verify backend and API key readiness."""
    load_dotenv(override=True)
    key = (os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY") or "").strip().strip("'").strip('"')
    is_valid = bool(key and key != "your_gemini_api_key_here")
    provider = "Groq (Llama 3.3)" if key.startswith("gsk_") else "Google Gemini"
    return {"status": "ok", "app": "HR CV Analyzer AI", "gemini_configured": is_valid, "groq_configured": is_valid, "provider": provider}


@app.post("/api/analyze", response_model=CVEvaluationReport)
async def analyze_cv(
    job_description: str = Form(..., description="Target Job Description text"),
    cv_file: UploadFile = File(..., description="Uploaded Candidate CV (PDF file)")
):
    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job Description is too short or empty. Please enter detailed job requirements."
        )

    if not cv_file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file (.pdf)."
        )

    file_bytes = await cv_file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if cv_file.filename.lower().endswith('.pdf'):
        cv_text = extract_text_from_pdf(file_bytes)
    else:
        cv_text = file_bytes.decode('utf-8', errors='ignore')

    if len(cv_text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract sufficient text from uploaded file."
        )

    return evaluate_cv_with_ai(cv_text=cv_text, job_description=job_description)


# Static File Serving
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={"message": "HR CV Analyzer API is running!"}
    )