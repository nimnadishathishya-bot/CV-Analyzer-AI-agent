# 💼 HR CV Analyzer AI - Full-Stack Web Application

An intelligent, full-stack recruitment web application designed for HR professionals and hiring managers to evaluate, score, and screen candidate resumes against any job description using Google Gemini and Groq AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg) ![Gemini API](https://img.shields.io/badge/Google--Gemini--API-gemini--3.8--flash-green.svg) ![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v3-38bdf8.svg)

---

## ✨ Features

- **⚡ Fast PDF Parsing**: Automatically extracts readable text from candidate resumes (`.pdf`) with multi-layer error-handling fallbacks.
- **🎯 AI-Powered Fit Scoring**: Calculates match percentage (0–100%) and categorizes fit (*Strong Fit*, *Moderate Fit*, *Needs Review*).
- **🏷️ Skills Gap Analysis**: Side-by-side comparison of **✅ Matched Strengths** vs **❌ Missing Requirements**.
- **🚩 Red Flags & Risks**: Automatically identifies employment gaps, qualification mismatches, or missing certifications.
- **💬 Tailored Interview Questions**: Generates 3–5 candidate-specific technical & behavioral interview questions with rationale and answers to look for.
- **🎨 Modern Recruiter UI**:
  - Light & Dark mode switch
  - 1-Click quick templates (*Python Dev*, *Frontend React*, *HR Specialist*)
  - 1-Click sample CV loader for testing
  - 1-Click "Copy Question" and "Copy Summary" actions

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hr-cv-analyzer-ai.git
cd hr-cv-analyzer-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/)).*

### 4. Run the Web App
#### Windows (1-Click):
Double-click `run_app.bat` to launch the server and open your browser automatically.

#### Terminal / Command Line:
```bash
uvicorn main:app --reload --port 8000
```
Open **`http://localhost:8000`** in your browser.

---

## 📁 Project Architecture

```
career AI/
├── main.py               # FastAPI backend with Gemini / Groq AI integration
├── run_app.bat           # 1-Click Windows desktop launcher
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git exclusion rules (protects API keys)
├── test_backend.py       # Automated unit & integration tests
├── static/               # Modern Frontend UI
│   ├── index.html        # Single-page application HTML
│   ├── app.js            # Frontend logic & API interaction
│   ├── styles.css        # Custom styles & animations
│   └── sample_cv.pdf     # Built-in demo candidate resume
└── sample_cvs/           # Extra sample resumes for testing
```

---

## 🧪 Running Tests
```bash
pytest test_backend.py
```

---

## 🛡️ License
MIT License. Free for commercial and personal use.
