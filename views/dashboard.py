"""
Dashboard View for Previous Year Question Paper Analyzer (PYQ Analyzer).
Displays executive KPI cards, topic spotlight banner, curriculum trends,
year-wise charts, quick action cards, and sample dataset preloader.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.priority_predictor import PriorityPredictor
from modules.visualization import (
    create_top_topics_bar_chart,
    create_topic_pie_chart,
    create_year_wise_line_chart
)
from utils.styling import render_kpi_card, render_topic_spotlight, render_section_header, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    # Hero Header Banner
    st.markdown("""
    <div class="app-header">
        <h1>📚 PYQ Analyzer Dashboard</h1>
        <p>AI-Powered Previous Year Question Paper Analytics, Empirical Recurrence Profiling & Study Prioritization</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch Data
    actual_subj = selected_subject if selected_subject != "All Subjects" else None
    kpis = db.get_kpis(subject=actual_subj)
    papers = db.get_papers(subject=actual_subj)
    questions = db.get_questions(subject=actual_subj)

    # Quick Action Bar (concise non-collapsing labels)
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        if st.button("📤 Upload Papers", use_container_width=True):
            st.switch_page("views/upload.py")
    with q_col2:
        if st.button("🎯 Important Topics", use_container_width=True):
            st.switch_page("views/important_topics.py")
    with q_col3:
        if st.button("📆 Study Planner", use_container_width=True):
            st.switch_page("views/study_planner.py")
    with q_col4:
        if st.button("📥 Export Reports", use_container_width=True):
            st.switch_page("views/export_reports.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Empty State & One-Click Demo Seeder
    if kpis["total_papers"] == 0:
        st.markdown("""
        <div class="info-callout">
            <h3 style="margin-top: 0; color: #1E3A8A;">👋 Welcome to PYQ Analyzer!</h3>
            <p>No question papers are indexed yet. You can upload university examination papers in <b>PDF</b>, <b>DOCX</b>, or <b>TXT</b> format, or load the pre-built 3-year DBMS sample dataset with one click below to explore all features instantly.</p>
        </div>
        """, unsafe_allow_html=True)

        col_seed, col_up = st.columns([1, 1])
        with col_seed:
            if st.button("🚀 Load Sample DBMS Dataset", type="primary", use_container_width=True):
                from sample_data.seed_data import seed_sample_database
                with st.spinner("Indexing 3 years of synthetic DBMS examination papers..."):
                    count = seed_sample_database(db)
                    st.success(f"Successfully loaded {count} questions across 2022, 2023, and 2024!")
                    st.rerun()
        with col_up:
            if st.button("📄 Upload Question Papers", use_container_width=True):
                st.switch_page("views/upload.py")

        st.markdown("---")

    # Executive KPI Cards Grid (4 evenly balanced columns)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Papers", kpis["total_papers"], "Indexed examination papers", "📄")
    with col2:
        render_kpi_card("Questions Extracted", kpis["total_questions"], "Individual questions", "❓")
    with col3:
        render_kpi_card("Unique Topics", kpis["unique_topics"], "Distinct syllabus concepts", "🏷️")
    with col4:
        render_kpi_card("Exam Cycles", kpis["total_years"], "Academic years analyzed", "📅")

    # Top Recurring Topic Spotlight Banner
    if kpis.get("most_repeated_topic") and kpis["most_repeated_topic"] != "None":
        render_topic_spotlight(
            topic=kpis["most_repeated_topic"],
            count=kpis["most_repeated_count"],
            years=kpis["total_years"],
            total_q=kpis["total_questions"]
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if questions:
        analyzer = TopicAnalyzer(questions)
        freq_summary = analyzer.get_topic_frequency_summary(exclude_unclassified=True)
        q_df = pd.DataFrame(questions)

        # Charts Section
        render_section_header("Curriculum Recurrence Profile", "Visual distribution of frequently repeated examination topics", "📊")
        chart_col1, chart_col2 = st.columns([3, 2])

        with chart_col1:
            fig_bar = create_top_topics_bar_chart(freq_summary, n=10)
            st.plotly_chart(fig_bar, use_container_width=True)

        with chart_col2:
            fig_pie = create_topic_pie_chart(freq_summary, max_slices=7)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Multi-Year Trend
        render_section_header("Historical Question Volume Trajectory", "Year-over-year question frequency trends", "📈")
        fig_line = create_year_wise_line_chart(q_df)
        st.plotly_chart(fig_line, use_container_width=True)

        # Bottom Cards: Top Priorities & Recently Processed Papers
        st.markdown("<br>", unsafe_allow_html=True)
        col_prio, col_recent = st.columns([3, 2])

        with col_prio:
            render_section_header("Top Historical Priorities", "Empirically highest recurring examination topics", "🎯")
            priorities = PriorityPredictor.calculate_priorities(freq_summary, total_years=kpis["total_years"])
            if not priorities.empty:
                display_cols = ["Topic", "Unit", "Frequency", "Years Appeared", "Priority Score", "Priority Category"]
                st.dataframe(
                    priorities[display_cols].head(5),
                    column_config={
                        "Priority Score": st.column_config.ProgressColumn(
                            "Yield Score",
                            format="%.1f",
                            min_value=0,
                            max_value=100
                        ),
                        "Frequency": st.column_config.NumberColumn("Questions"),
                        "Years Appeared": st.column_config.NumberColumn("Exam Years")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.write("No classified topics available.")

        with col_recent:
            render_section_header("Recently Uploaded Papers", "Status of indexed question papers", "📑")
            if papers:
                recent_df = pd.DataFrame(papers)[["filename", "subject", "academic_year", "question_count", "uploaded_at"]].head(5)
                recent_df.rename(columns={
                    "filename": "Filename",
                    "subject": "Subject",
                    "academic_year": "Year",
                    "question_count": "Questions",
                    "uploaded_at": "Uploaded"
                }, inplace=True)
                st.dataframe(recent_df, hide_index=True, use_container_width=True)
            else:
                st.write("No papers uploaded yet.")

    else:
        render_section_header("Application Capabilities", "Features designed for exam preparation", "💡")
        st.markdown("""
        - **1. Multi-Format Extraction**: Ingest `.pdf`, `.docx`, and `.txt` papers with automatic OCR for scanned documents.
        - **2. Intelligent Splitting**: Automatically extracts numbered questions, subquestions, and marks annotations.
        - **3. AI Taxonomy Classification**: Standardizes topics consistently across different years using OpenAI LLM or rule-based engine.
        - **4. Empirical Frequency Analysis**: Calculates recurring topic percentages and multi-year distribution matrices.
        - **5. Study Planning & Practice**: Generates day-by-day revision roadmaps and realistic practice exam papers.
        """)

if __name__ == "__main__" or True:
    render()
