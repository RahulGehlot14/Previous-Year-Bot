"""
Previous Year Question Paper Analyzer (PYQ Analyzer)
Main Streamlit Application Entrypoint.
Uses Streamlit 1.36+ st.navigation and st.Page for a modern, grouped,
professional sidebar with custom icons, section titles, and active subject scope.
"""

import streamlit as st
from config import APP_NAME, APP_FULL_NAME, APP_VERSION, APP_ICON
from database.db_manager import DatabaseManager
from utils.styling import load_custom_css

# Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Previous Year Question Paper Analyzer",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS theme
load_custom_css()

# Initialize Database Manager
if "db_manager" not in st.session_state:
    st.session_state["db_manager"] = DatabaseManager()

db = st.session_state["db_manager"]

# Sidebar Header & Global Controls
with st.sidebar:
    st.markdown(f"## {APP_ICON} {APP_NAME}")
    st.caption(f"{APP_FULL_NAME} • v{APP_VERSION}")
    st.markdown("---")

    # Global Subject Scope Filter
    all_stored_subjects = db.get_all_subjects()
    subject_options = ["All Subjects"] + all_stored_subjects
    current_active = st.session_state.get("active_subject", "All Subjects")
    active_idx = subject_options.index(current_active) if current_active in subject_options else 0

    chosen_subj = st.selectbox(
        "🎯 Active Subject Scope",
        options=subject_options,
        index=active_idx,
        help="Filters the analytics, charts, and question bank across all pages."
    )
    st.session_state["active_subject"] = chosen_subj

    # Sidebar Quick Metrics
    kpis = db.get_kpis(subject=chosen_subj if chosen_subj != "All Subjects" else None)
    c1, c2, c3 = st.columns(3)
    c1.metric("Papers", kpis["total_papers"])
    c2.metric("Questions", kpis["total_questions"])
    c3.metric("Topics", kpis["unique_topics"])

    st.markdown("---")

# Navigation Definition using st.Page and st.navigation
pages = {
    "Core Overview": [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("views/upload.py", title="Upload Papers", icon="📤"),
    ],
    "Topic Analytics": [
        st.Page("views/question_analysis.py", title="Question Analysis", icon="🔎"),
        st.Page("views/topic_frequency.py", title="Topic Frequency", icon="📈"),
        st.Page("views/year_analysis.py", title="Year-wise Analysis", icon="📅"),
    ],
    "Exam Preparation": [
        st.Page("views/important_topics.py", title="Important Topics", icon="🎯"),
        st.Page("views/question_bank.py", title="Question Bank & Flashcards", icon="🗃️"),
        st.Page("views/study_planner.py", title="AI Study Planner & Mock Exam", icon="📆"),
    ],
    "Export & Setup": [
        st.Page("views/export_reports.py", title="Export Reports", icon="📥"),
        st.Page("views/settings.py", title="Settings & Config", icon="⚙️"),
    ]
}

nav = st.navigation(pages)
nav.run()
