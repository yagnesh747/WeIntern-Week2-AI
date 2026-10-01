"""
app.py - WeIntern AI Resume Screening & Candidate Ranking System
================================================================
Task 2: Production-Grade Resume Screening Application built with
Streamlit, scikit-learn (TF-IDF + Cosine Similarity), and PDF parsing.

Features:
- Accurate entity extraction (strict name validation, professional experience tenure)
- Transparent 4-factor scoring: 50% Semantic, 35% Skills, 10% Edu, 5% Exp
- Separate Match % and Skill Match %
- Horizontal scrollable leaderboard table
- Export to CSV

Author  : WeIntern AI Internship Team
Task    : Week 2 - Task 2: Resume Screening AI
"""

import io
import os
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from matcher import ResumeMatcher
from resume_parser import ResumeParser
from skill_extractor import SkillExtractor

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Screening AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# Custom Light Design System CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide sidebar and its toggle arrow completely */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
    }
    /* Expand main content to full width */
    .main .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Header Container */
    .app-header {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .app-title {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        color: #64748b;
        font-size: 0.875rem;
        margin-top: 4px;
    }
    .badge-tag {
        background: #eef2ff;
        color: #4f46e5;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid #c7d2fe;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        text-align: left;
    }
    .metric-num {
        font-size: 1.75rem;
        font-weight: 700;
        color: #4f46e5;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    /* Horizontal Scrollable Table Wrapper */
    .table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
        margin-bottom: 16px;
    }
    
    /* Candidate Cards */
    .cand-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: border-color 0.15s ease;
    }
    .cand-card:hover {
        border-color: #cbd5e1;
    }
    .cand-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .cand-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    .cand-contact {
        font-size: 0.825rem;
        color: #64748b;
        margin-top: 2px;
    }
    .rank-badge {
        background: #4f46e5;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 999px;
    }
    .rank-badge.top-rank {
        background: #059669;
    }
    
    /* Score Breakdown Pill */
    .score-breakdown-pill {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 0.775rem;
        color: #475569;
        margin-top: 8px;
        line-height: 1.5;
    }
    
    /* Chips */
    .chip {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 3px 8px;
        border-radius: 6px;
        margin: 2px;
    }
    .chip-match {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .chip-missing {
        background: #fff1f2;
        color: #9f1239;
        border: 1px solid #fecdd3;
    }
    .chip-neutral {
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #e2e8f0;
    }
    
    /* Section Headers */
    .section-head {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin: 20px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Initialize Components (Cached)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_parser_and_matcher() -> tuple[ResumeParser, ResumeMatcher]:
    extractor = SkillExtractor()
    parser = ResumeParser(skill_extractor=extractor)
    matcher = ResumeMatcher(skill_extractor=extractor)
    return parser, matcher


parser, matcher = get_parser_and_matcher()

# Path helpers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")
SAMPLE_AIML_JD_PATH = os.path.join(SAMPLE_DATA_DIR, "sample_job_description.txt")
SAMPLE_JAVA_JD_PATH = os.path.join(SAMPLE_DATA_DIR, "sample_java_job_description.txt")
SAMPLE_RESUMES_DIR = os.path.join(SAMPLE_DATA_DIR, "sample_resumes")




# -----------------------------------------------------------------------------
# Header Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <div>
            <h1 class="app-title">📋 AI Resume Screening & Candidate Ranking</h1>
        </div>
        <div>
            <span class="badge-tag">50% Semantic + 35% Skills + 10% Edu + 5% Exp</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Step 1 & 2: Inputs (Job Description + Resumes)
# -----------------------------------------------------------------------------
col_jd, col_upload = st.columns([1, 1], gap="medium")

if "job_description_text" not in st.session_state:
    st.session_state["job_description_text"] = ""

with col_jd:
    st.markdown("### 1. Job Description")

    col_j1, col_j2 = st.columns(2)
    with col_j1:
        if st.button("📋 Load AI/ML JD", use_container_width=True):
            if os.path.exists(SAMPLE_AIML_JD_PATH):
                with open(SAMPLE_AIML_JD_PATH, "r", encoding="utf-8") as f:
                    st.session_state["job_description_text"] = f.read()
                st.success("Loaded AI/ML Engineer JD!")
    with col_j2:
        if st.button("☕ Load Java Developer JD", use_container_width=True):
            if os.path.exists(SAMPLE_JAVA_JD_PATH):
                with open(SAMPLE_JAVA_JD_PATH, "r", encoding="utf-8") as f:
                    st.session_state["job_description_text"] = f.read()
                st.success("Loaded Java Developer JD!")

    jd_text = st.text_area(
        label="Job Description Text",
        value=st.session_state["job_description_text"],
        height=260,
        placeholder="Paste your target job description requirements here...",
        help="Paste the job requirements, qualifications, and responsibilities.",
    )
    st.session_state["job_description_text"] = jd_text


with col_upload:
    st.markdown("### 2. Candidate Resumes")

    load_sample_resumes = st.checkbox(
        "⚡ Include Pre-Generated Sample Resumes (Java, AI, React, Full-Stack, etc.)",
        value=False,
        help="Loads realistic PDF resumes from sample_data/sample_resumes/ for instant testing.",
    )

    uploaded_files = st.file_uploader(
        "Upload Candidate Resumes (PDF format)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or multiple candidate PDF resumes.",
    )

    if load_sample_resumes:
        count = len([f for f in os.listdir(SAMPLE_RESUMES_DIR) if f.endswith('.pdf')]) if os.path.exists(SAMPLE_RESUMES_DIR) else 0
        st.info(f"{count} pre-generated PDF resumes will be included in the screening analysis.")


# -----------------------------------------------------------------------------
# Step 3: Analyze Action
# -----------------------------------------------------------------------------
st.markdown("---")
analyze_btn = st.button("🚀 Analyze & Rank Resumes", type="primary", use_container_width=True)

if analyze_btn:
    if not jd_text.strip():
        st.error("⚠️ Please provide a Job Description before analyzing.")
        st.stop()

    resumes_to_parse: List[Dict[str, Any]] = []

    # 1. From file uploader
    if uploaded_files:
        for up_file in uploaded_files:
            resumes_to_parse.append({
                "source": up_file,
                "filename": up_file.name,
            })

    # 2. From sample directory
    if load_sample_resumes:
        if os.path.exists(SAMPLE_RESUMES_DIR):
            for fname in sorted(os.listdir(SAMPLE_RESUMES_DIR)):
                if fname.lower().endswith(".pdf"):
                    fpath = os.path.join(SAMPLE_RESUMES_DIR, fname)
                    resumes_to_parse.append({
                        "source": fpath,
                        "filename": fname,
                    })

    if not resumes_to_parse:
        st.warning("⚠️ Please upload at least one PDF resume or check 'Include Pre-Generated Sample Resumes'.")
        st.stop()

    progress_bar = st.progress(0, text="Parsing candidate resumes...")
    parsed_resumes = []

    for i, item in enumerate(resumes_to_parse):
        pct = (i + 1) / len(resumes_to_parse)
        progress_bar.progress(pct, text=f"Parsing ({i+1}/{len(resumes_to_parse)}): {item['filename']}")
        parsed = parser.parse(item["source"], filename=item["filename"])
        parsed_resumes.append(parsed)

    progress_bar.progress(1.0, text="Computing 4-factor scoring and ranking...")

    try:
        results = matcher.analyze(job_description=jd_text, parsed_resumes=parsed_resumes)
        st.session_state["screening_results"] = results
        progress_bar.empty()
        st.success(f"Successfully screened and ranked {len(parsed_resumes)} candidates!")
    except Exception as exc:
        progress_bar.empty()
        st.error(f"Analysis failed: {exc}")
        st.stop()


# -----------------------------------------------------------------------------
# Step 4: Display Results Dashboard
# -----------------------------------------------------------------------------
if "screening_results" in st.session_state:
    results = st.session_state["screening_results"]
    candidates = results["candidates"]
    summary = results["summary"]
    df = results["dataframe"]
    jd_skills = results["jd_skills"]

    st.markdown("<h2 class='section-head'>📊 Screening Overview & Metrics</h2>", unsafe_allow_html=True)

    # 4 Key Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num">{summary['total_candidates']}</div>
                <div class="metric-label">Resumes Screened</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num">{summary['top_score']:.1f}%</div>
                <div class="metric-label">Top Match Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num">{summary['average_score']:.1f}%</div>
                <div class="metric-label">Average Match Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-num">{summary['high_matches']}</div>
                <div class="metric-label">Strong Fits (&ge;70%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab_rank, tab_cards, tab_summary = st.tabs(
        ["🏆 Leaderboard Table", "👤 Candidate Deep-Dive Cards", "📈 Executive Summary & Report"]
    )

    # TAB 1: Ranking Table (Horizontally Scrollable)
    with tab_rank:
        st.markdown("### Candidate Leaderboard (Highest to Lowest Match)")
        
        display_cols = [
            "Rank", "Candidate Name", "Match %", "Skill Match %",
            "Matching Skills", "Missing Skills", "Experience", "Education"
        ]
        
        # Streamlit dataframe with horizontal scrolling support
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
        )

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Full Screening Results as CSV",
            data=csv_buffer.getvalue(),
            file_name="weintern_resume_screening_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # TAB 2: Detailed Candidate Cards
    with tab_cards:
        st.markdown("### Detailed Candidate Analysis")

        for cand in candidates:
            rank = cand["rank"]
            is_top = rank == 1
            badge_class = "rank-badge top-rank" if is_top else "rank-badge"

            match_pct = cand.get("match_percentage", 0.0)
            skill_pct = cand.get("skill_match_percentage", 0.0)
            breakdown = cand.get("score_breakdown") or {}
            sem_sim = float(breakdown.get("semantic_similarity", breakdown.get("semantic_score", 0.0)))
            skl_mat = float(breakdown.get("skill_match", breakdown.get("skill_score", 0.0)))
            edu_rel = float(breakdown.get("education_relevance", breakdown.get("education_score", 0.0)))
            exp_rel = float(breakdown.get("experience_relevance", breakdown.get("experience_score", 0.0)))

            matching_chips = "".join(
                f"<span class='chip chip-match'>✓ {s}</span>" for s in cand.get("matching_skills", [])
            ) if cand.get("matching_skills") else "<span style='color:#94a3b8; font-size:0.8rem;'>No exact matches</span>"

            missing_chips = "".join(
                f"<span class='chip chip-missing'>✗ {s}</span>" for s in cand.get("missing_skills", [])
            ) if cand.get("missing_skills") else "<span style='color:#94a3b8; font-size:0.8rem;'>None</span>"

            edu_text = " • ".join(cand.get("education", [])) if cand.get("education") else "Not specified"

            with st.container():
                st.markdown(
                    f"""
                    <div class="cand-card">
                        <div class="cand-header">
                            <div>
                                <h3 class="cand-name">{cand.get('name', 'Name Not Detected')}</h3>
                                <div class="cand-contact">
                                    📧 {cand.get('email', 'Not detected')} &nbsp;|&nbsp; 📞 {cand.get('phone', 'Not detected')} &nbsp;|&nbsp; 📁 {cand.get('filename', 'Resume.pdf')}
                                </div>
                            </div>
                            <span class="{badge_class}">Rank #{rank}</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                c_score, c_skills = st.columns([1, 2])
                with c_score:
                    st.metric(label="Overall Match %", value=f"{match_pct:.1f}%")
                    st.progress(min(1.0, max(0.0, match_pct / 100.0)))
                    st.caption(f"Required Skill Match: **{skill_pct:.1f}%** ({len(cand.get('matching_skills', []))} of {summary['jd_skills_count']} JD skills)")

                    st.markdown(
                        f"""
                        <div class="score-breakdown-pill">
                            <b>Score Breakdown:</b><br>
                            • 50% Semantic Sim: <b>{sem_sim:.1f}%</b><br>
                            • 35% Required Skills: <b>{skl_mat:.1f}%</b><br>
                            • 10% Education: <b>{edu_rel:.1f}%</b><br>
                            • 5% Experience: <b>{exp_rel:.1f}%</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"**Experience:** {cand.get('experience_summary', 'Fresher / 0 years')}")
                    st.markdown(f"**Education:** {edu_text}")

                with c_skills:
                    st.markdown("**Matching Skills Found in Job Description:**")
                    st.markdown(matching_chips, unsafe_allow_html=True)

                    st.markdown("<div style='margin-top:8px;'><b>Missing Skills (Required by JD):</b></div>", unsafe_allow_html=True)
                    st.markdown(missing_chips, unsafe_allow_html=True)

                with st.expander(f"🔍 View Extracted Resume Text for {cand['name']}"):
                    st.text(cand["raw_text"][:2000] + ("..." if len(cand["raw_text"]) > 2000 else ""))

                st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3: Executive Summary & Recommendation
    with tab_summary:
        st.markdown("### Executive Screening Summary")

        top_cand = candidates[0] if candidates else None

        if top_cand:
            st.info(
                f"""
                **Top Recommendation**: **{top_cand['name']}** ranked #1 with an **overall match score of {top_cand['match_percentage']:.1f}%**.
                Matches {len(top_cand['matching_skills'])} key JD skills with {top_cand['experience_summary']}.
                """
            )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("#### Candidate Fit Breakdown")
            breakdown_data = pd.DataFrame({
                "Fit Level": ["Strong Fit (≥70%)", "Potential Match (50–69%)", "Low Match (<50%)"],
                "Candidates": [summary["high_matches"], summary["moderate_matches"], summary["low_matches"]],
            })
            st.dataframe(breakdown_data, use_container_width=True, hide_index=True)

        with col_b2:
            st.markdown("#### Most Common Missing Skills Across Candidates")
            if summary["top_missing_skills"]:
                missing_df = pd.DataFrame(
                    summary["top_missing_skills"],
                    columns=["Skill", "Candidates Missing Skill"]
                )
                st.dataframe(missing_df, use_container_width=True, hide_index=True)
            else:
                st.write("No missing skills recorded across candidate pool.")

        st.markdown("---")
        st.markdown("#### Skills Detected in Job Description:")
        if jd_skills:
            jd_chips = "".join(f"<span class='chip chip-neutral'>{s}</span>" for s in jd_skills)
            st.markdown(jd_chips, unsafe_allow_html=True)
        else:
            st.write("No specific technical keywords detected in Job Description.")
