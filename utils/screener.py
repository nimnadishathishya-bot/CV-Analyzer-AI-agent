import json
import os
import re
from typing import Dict, Any, List, Optional

def _clean_json_string(text: str) -> str:
    """
    Remove markdown code block syntax if present in the LLM response text.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text

def evaluate_cv(cv_text: str, job_description: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluates candidate CV text against Job Description using Gemini API.
    Enforces unbiased evaluation (ignores name, gender, age, photo, nationality).
    Returns structured dictionary with keys:
    - name, score, matched_skills, missing_skills, years_experience, portfolio_link, summary
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not effective_api_key:
        raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or enter key in sidebar.")

    system_prompt = (
        "You are an expert HR AI talent acquisition screener. "
        "Your task is to analyze candidate CV text against a Job Description and output structured JSON format.\n\n"
        "STRICT UNBIASED SCORING RULES:\n"
        "- IGNORE name, gender, age, photo, ethnicity, and nationality when determining the numerical score.\n"
        "- Calculate score (0-100) strictly based on matching skills, technical capabilities, years of relevant experience, "
        "education relevancy, and portfolio requirements.\n"
        "- Extract the candidate's actual name if present in the CV text for display purposes only (do not factor it into score).\n"
        "- Extract portfolio or work links (e.g., GitHub, Behance, Dribbble, LinkedIn, personal website, drive link) if present.\n\n"
        "Return ONLY a JSON object with this exact structure:\n"
        "{\n"
        '  "name": "Candidate Full Name or Unknown Candidate",\n'
        '  "score": 85,\n'
        '  "matched_skills": ["Skill 1", "Skill 2"],\n'
        '  "missing_skills": ["Skill 3"],\n'
        '  "years_experience": "X years",\n'
        '  "portfolio_link": "URL or empty string",\n'
        '  "summary": "Concise 2-3 sentence rationale of score and suitability."\n'
        "}"
    )

    user_prompt = f"""
JOB DESCRIPTION:
{job_description}

CANDIDATE CV TEXT:
{cv_text}
"""

    response_text = ""
    
    # Try google-genai package first
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=effective_api_key)
        
        # Models to try in priority order
        model_name = "gemini-2.5-flash"
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            response_text = res.text
        except Exception:
            # Fallback model
            res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            response_text = res.text

    except (ImportError, Exception) as primary_err:
        # Fallback to google.generativeai
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=effective_api_key)
            model = genai_legacy.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            response_text = res.text
        except Exception as legacy_err:
            raise RuntimeError(f"Failed to communicate with LLM API: {str(primary_err)} | {str(legacy_err)}")

    clean_json = _clean_json_string(response_text)
    try:
        data = json.loads(clean_json)
        # Ensure default fields
        data["name"] = str(data.get("name", "Unknown Candidate")).strip()
        data["score"] = int(data.get("score", 0))
        data["matched_skills"] = list(data.get("matched_skills", []))
        data["missing_skills"] = list(data.get("missing_skills", []))
        data["years_experience"] = str(data.get("years_experience", "N/A")).strip()
        data["portfolio_link"] = str(data.get("portfolio_link", "") or "").strip()
        data["summary"] = str(data.get("summary", "No summary provided.")).strip()
        return data
    except json.JSONDecodeError as err:
        raise ValueError(f"LLM returned invalid JSON response: {clean_json}") from err

def generate_interview_questions(
    candidate_data: Dict[str, Any],
    job_description: str,
    api_key: Optional[str] = None
) -> List[str]:
    """
    Generates 3 to 5 customized interview questions for a given candidate based on their CV match details.
    """
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not effective_api_key:
        raise ValueError("Gemini API key is required.")

    prompt = f"""
You are an expert HR interviewer. Generate 3 to 5 highly relevant, specific interview questions for this candidate.
Tailor the questions to probe their matched skills, evaluate their missing skills, and verify their claimed experience level for the job.

JOB DESCRIPTION:
{job_description}

CANDIDATE EVALUATION:
Name: {candidate_data.get('name')}
Score: {candidate_data.get('score')}/100
Matched Skills: {', '.join(candidate_data.get('matched_skills', []))}
Missing Skills: {', '.join(candidate_data.get('missing_skills', []))}
Years of Experience: {candidate_data.get('years_experience')}
Summary: {candidate_data.get('summary')}

Return ONLY a JSON list of strings (e.g. ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]).
"""

    response_text = ""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=effective_api_key)
        try:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            response_text = res.text
        except Exception:
            res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            response_text = res.text

    except Exception:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=effective_api_key)
        model = genai_legacy.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(prompt)
        response_text = res.text

    clean_json = _clean_json_string(response_text)
    try:
        questions = json.loads(clean_json)
        if isinstance(questions, list):
            return [str(q).strip() for q in questions if str(q).strip()]
        elif isinstance(questions, dict) and "questions" in questions:
            return [str(q).strip() for q in questions["questions"] if str(q).strip()]
        return ["Describe your past relevant project experience.", "How do you handle key deliverables under deadline?"]
    except Exception:
        # Fallback question parsing
        lines = [line.strip("- *1234567890. ") for line in response_text.split("\n") if "?" in line]
        return lines[:5] if lines else [
            "Can you explain your experience with the key skills listed on your CV?",
            "How have you overcome challenges in your previous roles?",
            "Can you walk us through a project in your portfolio?"
        ]
