import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from utils.extractor import extract_text_from_file
from utils.screener import evaluate_cv, generate_interview_questions

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="CV Screener for HR - AI Talent Screening",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Glassmorphism & Sleek HR Custom CSS
CUSTOM_CSS = """
<style>
    /* Dark enterprise theme colors */
    :root {
        --bg-color: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --text-color: #f8fafc;
        --muted-text: #94a3b8;
    }

    /* Main container background */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #0f172a 50%, #1e1b4b 100%);
        color: var(--text-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header styling */
    .main-header {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.36);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: var(--muted-text);
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* KPI Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }

    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--muted-text);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
    }

    /* Candidate Detail Card */
    .candidate-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    /* Score Badges */
    .score-badge-high {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 6px 16px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }

    .score-badge-medium {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 6px 16px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 12px rgba(245, 158, 11 0.4);
    }

    .score-badge-low {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 6px 16px;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }

    /* Skill Pills */
    .skill-pill-matched {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .skill-pill-missing {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #fca5a5;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .experience-badge {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #93c5fd;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
    }

    .unbiased-note {
        font-size: 0.8rem;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 3px solid #3b82f6;
        margin-top: 10px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
if "results" not in st.session_state:
    st.session_state.results = []
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = {}

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/3b82f6/resume.png", width=60)
    st.title("Settings & Config")
    
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_api_key,
        type="password",
        help="Leave blank to use GEMINI_API_KEY environment variable if configured."
    )
    
    effective_api_key = api_key_input.strip() or env_api_key
    
    if effective_api_key:
        st.success("✓ API Key Connected", icon="✅")
    else:
        st.warning("⚠️ No API Key found. Please enter key above or set GEMINI_API_KEY env variable.", icon="🔑")
        
    st.markdown("---")
    st.subheader("Filter & Display")
    min_score_filter = st.slider("Minimum Match Score Filter", 0, 100, 0, step=5)
    
    st.markdown("---")
    st.markdown("### 🔒 Unbiased Screening Policy")
    st.caption(
        "This tool automatically excludes candidate name, gender, age, photo, and nationality "
        "from the scoring algorithm to ensure fair, merit-based screening."
    )
    
    if st.button("Clear Results"):
        st.session_state.results = []
        st.session_state.interview_questions = {}
        st.rerun()

# Main Header
st.markdown("""
<div class="main-header">
    <h1>💼 CV Screener for HR</h1>
    <p>AI-Powered Resume Evaluation, Candidate Ranking & Unbiased Skill Matching</p>
</div>
""", unsafe_allow_html=True)

# Input Section (Two Columns)
col_jd, col_cv = st.columns([1, 1], gap="large")

with col_jd:
    st.subheader("1. Job Description")
    
    sample_jd_text = (
        "Graphic Designer: Expert in Photoshop, Illustrator, and Figma. "
        "Requires 3+ years of professional experience, UI/UX design capabilities, and a strong digital portfolio."
    )
    
    if st.button("💡 Load Sample Job Description"):
        st.session_state.jd_input = sample_jd_text
        
    job_description = st.text_area(
        "Paste the Job Requirements:",
        value=st.session_state.get("jd_input", ""),
        height=220,
        placeholder="Paste role requirements, required technical skills, experience needed, and qualifications..."
    )

with col_cv:
    st.subheader("2. Upload Candidate Resumes")
    uploaded_files = st.file_uploader(
        "Upload Resume Files (PDF or DOCX):",
        type=["pdf", "docx", "doc", "txt"],
        accept_multiple_files=True,
        help="You can drag and drop multiple candidate resumes at once."
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected for analysis.")

st.markdown("---")

# Screening Action Button
if st.button("🚀 Analyze & Rank Candidates", type="primary", use_container_width=True):
    if not job_description.strip():
        st.error("Please provide a Job Description before running analysis.")
    elif not uploaded_files:
        st.error("Please upload at least one candidate resume (PDF or DOCX).")
    elif not effective_api_key:
        st.error("Gemini API key is required. Please set GEMINI_API_KEY environment variable or enter it in the sidebar.")
    else:
        results = []
        progress_bar = st.progress(0, text="Initializing text extraction...")
        status_box = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            progress = (idx + 1) / len(uploaded_files)
            file_name = uploaded_file.name
            status_box.markdown(f"⏳ **Processing ({idx+1}/{len(uploaded_files)}):** `{file_name}`...")
            
            try:
                # Read bytes and extract text
                file_bytes = uploaded_file.read()
                cv_text = extract_text_from_file(file_name, file_bytes)
                
                if not cv_text or len(cv_text.strip()) < 20:
                    st.warning(f"Could not extract sufficient text from `{file_name}`. File might be scanned/empty.")
                    continue
                
                # Evaluate via LLM API
                evaluation = evaluate_cv(
                    cv_text=cv_text,
                    job_description=job_description,
                    api_key=effective_api_key
                )
                evaluation["file_name"] = file_name
                results.append(evaluation)
                
            except Exception as e:
                st.error(f"Error processing `{file_name}`: {str(e)}")
            
            progress_bar.progress(progress, text=f"Analyzed {idx+1} of {len(uploaded_files)} CVs...")
            
        status_box.success("✅ Analysis completed successfully!")
        
        # Sort results descending by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        st.session_state.results = results
        st.session_state.interview_questions = {}

# Results Dashboard Output
if st.session_state.results:
    all_results = st.session_state.results
    
    # Filter by minimum score
    filtered_results = [r for r in all_results if r.get("score", 0) >= min_score_filter]
    
    # KPI Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    total_count = len(all_results)
    top_score = all_results[0].get("score", 0) if all_results else 0
    top_name = all_results[0].get("name", "N/A") if all_results else "N/A"
    avg_score = round(sum(r.get("score", 0) for r in all_results) / max(total_count, 1), 1)
    qualified_count = len([r for r in all_results if r.get("score", 0) >= 70])
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{total_count}</div>
            <div class="metric-label">CVs Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{top_score}%</div>
            <div class="metric-label">Top Score ({top_name[:12]}...)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{avg_score}%</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{qualified_count}</div>
            <div class="metric-label">High-Fit Candidates (70%+)</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Dashboard Tabs
    tab_rank, tab_details, tab_export = st.tabs(["🏆 Ranked Leaderboard", "📑 Candidate Deep Dive & Questions", "📥 Export Report"])
    
    # TAB 1: Ranked Leaderboard Table
    with tab_rank:
        st.subheader("Candidate Rankings (Sorted by Match Score)")
        
        if not filtered_results:
            st.info(f"No candidates match the current minimum score filter ({min_score_filter}%). Adjust sidebar slider.")
        else:
            table_data = []
            for rank, r in enumerate(filtered_results, start=1):
                table_data.append({
                    "Rank": f"#{rank}",
                    "Candidate Name": r.get("name"),
                    "Match Score": f"{r.get('score')}/100",
                    "Experience": r.get("years_experience"),
                    "Matched Skills": ", ".join(r.get("matched_skills", [])) or "None",
                    "Missing Skills": ", ".join(r.get("missing_skills", [])) or "None",
                    "Portfolio": r.get("portfolio_link") or "N/A",
                    "File": r.get("file_name")
                })
                
            df = pd.DataFrame(table_data)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Match Score": st.column_config.ProgressColumn(
                        "Match Score",
                        format="%s",
                        min_value=0,
                        max_value=100,
                    ),
                    "Portfolio": st.column_config.LinkColumn("Portfolio Link")
                },
                hide_index=True
            )
            
    # TAB 2: Detailed Candidate Breakdown
    with tab_details:
        st.subheader("Candidate Evaluation Cards")
        
        for idx, cand in enumerate(filtered_results, start=1):
            score = cand.get("score", 0)
            if score >= 80:
                badge_class = "score-badge-high"
            elif score >= 60:
                badge_class = "score-badge-medium"
            else:
                badge_class = "score-badge-low"
                
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="margin: 0; color: #f8fafc; font-size: 1.5rem;">#{idx} {cand.get('name')}</h2>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">Source File: <code>{cand.get('file_name')}</code></p>
                        </div>
                        <div class="{badge_class}">
                            Score: {score}/100
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_info1, col_info2 = st.columns([1, 1])
                
                with col_info1:
                    st.markdown("**Matched Skills:**")
                    matched = cand.get("matched_skills", [])
                    if matched:
                        pills = "".join([f'<span class="skill-pill-matched">✓ {s}</span>' for s in matched])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.write("None identified.")
                        
                    st.markdown("**Missing / Desirable Skills:**")
                    missing = cand.get("missing_skills", [])
                    if missing:
                        pills = "".join([f'<span class="skill-pill-missing">✗ {s}</span>' for s in missing])
                        st.markdown(pills, unsafe_allow_html=True)
                    else:
                        st.write("None identified.")

                with col_info2:
                    st.markdown(f"**Experience Level:** <span class='experience-badge'>⏱️ {cand.get('years_experience')}</span>", unsafe_allow_html=True)
                    
                    port_url = cand.get("portfolio_link", "")
                    if port_url and port_url != "N/A" and ("http" in port_url or "www" in port_url):
                        st.markdown(f"**Portfolio:** [🔗 {port_url}]({port_url})")
                    elif port_url:
                        st.markdown(f"**Portfolio / Link:** {port_url}")
                    else:
                        st.markdown("**Portfolio:** Not specified in CV")

                st.markdown(f"**Summary Evaluation:** {cand.get('summary')}")
                st.markdown('<div class="unbiased-note">🛡️ <i>Scored strictly on skills and experience. Demographic attributes ignored.</i></div>', unsafe_allow_html=True)

                # Interview Questions Button & Generator
                cand_key = f"cand_{idx}_{cand.get('file_name')}"
                if st.button(f"❓ Generate 3-5 Interview Questions for {cand.get('name')}", key=f"btn_{cand_key}"):
                    with st.spinner("Generating targeted interview questions..."):
                        try:
                            questions = generate_interview_questions(
                                candidate_data=cand,
                                job_description=job_description,
                                api_key=effective_api_key
                            )
                            st.session_state.interview_questions[cand_key] = questions
                        except Exception as err:
                            st.error(f"Failed to generate questions: {str(err)}")
                            
                # Display questions if generated
                if cand_key in st.session_state.interview_questions:
                    questions_list = st.session_state.interview_questions[cand_key]
                    st.success(f"Generated {len(questions_list)} Interview Questions:")
                    for q_num, q_text in enumerate(questions_list, start=1):
                        st.write(f"**Q{q_num}:** {q_text}")
                        
                st.markdown("---")

    # TAB 3: Export Report
    with tab_export:
        st.subheader("Export Results")
        st.write("Download candidate screening data for record keeping or team sharing.")
        
        # Prepare JSON and CSV downloads
        export_json = json.dumps(all_results, indent=2)
        export_df = pd.DataFrame(all_results)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="📥 Download Results as CSV",
                data=export_df.to_csv(index=False),
                file_name="cv_screener_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c2:
            st.download_button(
                label="📥 Download Results as JSON",
                data=export_json,
                file_name="cv_screener_results.json",
                mime="application/json",
                use_container_width=True
            )
