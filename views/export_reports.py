"""
Export Reports View for Previous Year Question Paper Analyzer.
Provides instant downloads for:
- PDF (Comprehensive ReportLab publication-ready report)
- Excel (.xlsx multi-worksheet report)
- CSV (Questions and Topic Frequencies)
- JSON (Structured Question Classifications)
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.priority_predictor import PriorityPredictor
from modules.report_generator import ReportGenerator
from utils.styling import render_section_header, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Export Reports & Datasets", "Download comprehensive analytics, question banks, and publication-ready reports", "📥")

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    subj_filter = st.selectbox("Select Subject for Export", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="exp_subj")

    actual_subj = subj_filter if subj_filter != "All Subjects" else None
    questions = db.get_questions(subject=actual_subj)
    kpis = db.get_kpis(subject=actual_subj)

    if not questions:
        st.info("No question data found for this subject. Upload papers or seed sample data before generating reports.")
        col_demo, col_up = st.columns([1, 1])
        with col_demo:
            if st.button("🚀 Load Sample DBMS Dataset", key="btn_seed_exp", type="primary", use_container_width=True):
                from sample_data.seed_data import seed_sample_database
                count = seed_sample_database(db)
                st.success(f"Successfully loaded {count} questions! Refreshing report view...")
                st.rerun()
        with col_up:
            if st.button("📄 Upload Question Papers", key="btn_up_exp", use_container_width=True):
                st.switch_page("views/upload.py")
        return

    analyzer = TopicAnalyzer(questions)
    freq_summary = analyzer.get_topic_frequency_summary(exclude_unclassified=False)
    year_distribution = analyzer.get_year_wise_distribution(exclude_unclassified=False)
    priorities = PriorityPredictor.calculate_priorities(freq_summary, total_years=kpis.get("total_years", 1))

    # Metric Banner
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Subject", subj_filter)
    col_m2.metric("Questions Ready", len(questions))
    col_m3.metric("Topics Analyzed", len(freq_summary))
    col_m4.metric("Exam Years", kpis.get("total_years", 0))

    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("Select Export Format", "Download high-resolution documents or machine-readable datasets", "📦")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #1E40AF;">📄 PDF Analysis Report</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0 0 12px 0;">Publication-quality document containing executive metadata, KPI summary, topic frequency breakdown, priority recommendations, and preparation guidance.</p>
        </div>
        """, unsafe_allow_html=True)

        pdf_bytes = ReportGenerator.generate_pdf_report(
            subject=subj_filter,
            kpis=kpis,
            topic_summary_df=freq_summary,
            priorities_df=priorities
        )
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"PYQ_Analysis_Report_{subj_filter.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #047857;">📊 Excel Workbook (.xlsx)</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0 0 12px 0;">5 multi-formatted worksheets: Executive Summary, Topic Frequency, Priority Recommendations, Year-wise Distribution Matrix, and Full Question Bank.</p>
        </div>
        """, unsafe_allow_html=True)

        excel_bytes = ReportGenerator.generate_excel_report(
            questions=questions,
            topic_summary_df=freq_summary,
            priorities_df=priorities,
            year_distribution_df=year_distribution
        )
        st.download_button(
            label="⬇️ Download Excel Workbook",
            data=excel_bytes,
            file_name=f"PYQ_Analysis_Report_{subj_filter.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col2:
        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #B45309;">📝 Tabular CSV Datasets</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0 0 12px 0;">Lightweight tabular datasets suitable for spreadsheet analysis, data science pipelines, and custom statistical evaluation.</p>
        </div>
        """, unsafe_allow_html=True)

        csv_q = ReportGenerator.generate_csv_questions(questions)
        st.download_button(
            label="⬇️ Download Questions CSV",
            data=csv_q,
            file_name=f"pyq_questions_{subj_filter.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        csv_t = ReportGenerator.generate_csv_topics(freq_summary)
        st.download_button(
            label="⬇️ Download Topic Frequencies CSV",
            data=csv_t,
            file_name=f"pyq_topic_frequency_{subj_filter.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #4338CA;">📦 JSON Classification Schema</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin: 0 0 12px 0;">Standardized JSON array schema containing question IDs, bloom taxonomy levels, difficulty ratings, and topic hierarchies.</p>
        </div>
        """, unsafe_allow_html=True)

        json_q = ReportGenerator.generate_json_questions(questions)
        st.download_button(
            label="⬇️ Download JSON Schema",
            data=json_q,
            file_name=f"pyq_questions_{subj_filter.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__" or True:
    render()
