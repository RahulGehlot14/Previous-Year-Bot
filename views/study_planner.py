"""
Study Planner & Mock Exam View for Previous Year Question Paper Analyzer.
Provides:
1. Personalized day-by-day revision roadmap weighted by topic priority.
2. University-style mock examination paper generator.
3. Cross-year recurring question similarity engine.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.priority_predictor import PriorityPredictor
from modules.study_planner import StudyPlanner
from modules.mock_exam_generator import MockExamGenerator
from modules.similarity_engine import SimilarityEngine
from utils.styling import render_section_header, render_timeline_node, get_priority_badge_html, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("AI Study Planner & Mock Exam Generator", "Smart preparation roadmaps, mock examination simulations, and recurring question patterns", "📅")

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    subj_filter = st.selectbox("Active Subject", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="sp_subj")

    questions = db.get_questions(subject=subj_filter if subj_filter != "All Subjects" else None)
    kpis = db.get_kpis(subject=subj_filter if subj_filter != "All Subjects" else None)

    if not questions:
        st.info("No questions found for this subject. Please upload past question papers or seed sample data.")
        return

    analyzer = TopicAnalyzer(questions)
    freq_summary = analyzer.get_topic_frequency_summary(exclude_unclassified=True)
    priorities = PriorityPredictor.calculate_priorities(freq_summary, total_years=kpis.get("total_years", 1))

    tab_plan, tab_mock, tab_patterns = st.tabs([
        "📆 Revision Roadmap",
        "📝 Mock Exam Generator",
        "🔍 Recurring Question Patterns"
    ])

    # Tab 1: AI Revision Roadmap
    with tab_plan:
        render_section_header("Revision Schedule Generator", "Weighted allocation based on historical priority score", "⏳")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            today = date.today()
            exam_target = st.date_input(
                "Target Examination Date",
                value=today + timedelta(days=14),
                min_value=today + timedelta(days=1),
                max_value=today + timedelta(days=90),
                key="plan_exam_date"
            )
        with col_d2:
            daily_study_hours = st.slider("Daily Study Commitment (Hours)", min_value=1.0, max_value=8.0, value=3.0, step=0.5, key="plan_hours")

        plan = StudyPlanner.generate_plan(
            priorities_df=priorities,
            exam_date=exam_target,
            start_date=today,
            daily_hours=daily_study_hours
        )

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Days Remaining", f"{plan['total_days']} Days")
        col_m2.metric("Total Study Hours", f"{plan['total_study_hours']} Hrs")
        col_m3.metric("Exam Date", plan["exam_date"])

        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("Day-by-Day Study Schedule", "Sequential roadmap to master high-yield topics first", "📋")

        for d in plan["days"]:
            badge = get_priority_badge_html(d.get("priority_category", "Medium Priority"))
            details_text = f"**Target Time:** `{d['target_hours']} hours` | **Unit:** `{d['unit']}`<br>{d['task']}"
            render_timeline_node(
                day_label=f"Day {d['day_number']} — {d['date']}",
                title=f"{d['topic']} ({d['type']})",
                details=details_text,
                badge_html=badge
            )

    # Tab 2: Mock Exam Generator
    with tab_mock:
        render_section_header("University Mock Examination Generator", "Synthesize balanced practice papers from past question banks", "🎓")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            target_marks = st.selectbox("Total Examination Marks", options=[50, 75, 100], index=2, key="mock_marks")
        with col_p2:
            target_duration = st.selectbox("Exam Duration", options=["2 Hours", "3 Hours"], index=1, key="mock_dur")
        with col_p3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            gen_btn = st.button("🎲 Generate Mock Paper", type="primary", use_container_width=True, key="btn_gen_mock")

        if gen_btn or "current_mock_exam" not in st.session_state:
            dur_num = 3 if "3" in target_duration else 2
            st.session_state["current_mock_exam"] = MockExamGenerator.generate_mock_paper(
                questions=questions,
                subject=subj_filter if subj_filter != "All Subjects" else "Curriculum Composite",
                total_marks=target_marks,
                duration_hours=dur_num
            )

        mock = st.session_state["current_mock_exam"]

        if "error" in mock:
            st.error(mock["error"])
        else:
            st.markdown(f"""
            <div class="mock-exam-container">
                <div class="mock-exam-header">
                    <div class="mock-exam-title">{mock['title']}</div>
                    <div class="mock-exam-meta">
                        <span>Time: {mock['duration']}</span>
                        <span>Max Marks: {mock['total_marks']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### Instructions to Candidates:")
            for inst in mock["instructions"]:
                st.caption(inst)

            st.markdown("---")

            for q in mock["questions"]:
                marks_str = f"[{int(q.get('assigned_marks', 10))} Marks]"
                with st.container():
                    col_q_text, col_q_marks = st.columns([5, 1])
                    with col_q_text:
                        st.markdown(f"**{q['mock_question_number']}.** {q['question_text']}")
                        st.caption(f"Topic: {q.get('topic', 'General')} • Unit: {q.get('unit', 'Unit 1')} • Bloom: {q.get('bloom_level', 'Understand')}")
                    with col_q_marks:
                        st.markdown(f"**{marks_str}**")
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #E2E8F0;'>", unsafe_allow_html=True)

    # Tab 3: Question Patterns
    with tab_patterns:
        render_section_header("Cross-Year Recurring Question Analysis", "Discover which question wordings are repeatedly reused across years", "🔁")

        sim_pairs = SimilarityEngine.find_cross_year_duplicates(questions, threshold=0.35)

        if not sim_pairs:
            st.info("No strong recurring question patterns detected across different years yet. Upload papers from 2 or more years to discover patterns.")
        else:
            st.markdown(f"**Identified {len(sim_pairs)} recurring question templates across different academic cycles:**")

            for pair in sim_pairs[:10]:
                with st.expander(f"**{pair['topic']}** — {pair['similarity_pct']}% Wording Similarity between {pair['q1_year']} and {pair['q2_year']}"):
                    col_yr1, col_yr2 = st.columns(2)
                    with col_yr1:
                        st.markdown(f"**Exam Year {pair['q1_year']} ({pair['q1_number']})**")
                        st.info(pair["q1_text"])
                    with col_yr2:
                        st.markdown(f"**Exam Year {pair['q2_year']} ({pair['q2_number']})**")
                        st.success(pair["q2_text"])
                    st.caption(f"Notice how examiners test '{pair['topic']}' with nearly identical phrasing across multiple years.")

if __name__ == "__main__" or True:
    render()
