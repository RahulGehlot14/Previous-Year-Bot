"""
Important Topics View for Previous Year Question Paper Analyzer.
Calculates historical priority scores, classifies topics into Very High, High, Medium,
and Low Priority, provides revision tips, and lists related past questions.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.priority_predictor import PriorityPredictor
from modules.visualization import create_priority_distribution_chart
from utils.styling import render_section_header, get_priority_badge_html, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Important Topics & Priority Recommendations", "Prioritize topics for study based on empirical historical examination trends", "🎯")

    st.markdown("""
    <div class="info-callout">
        <b>💡 How Priority Scores Are Calculated:</b><br>
        Priority Score = <code>(Topic Frequency / Maximum Frequency &times; 60) + (Years Appeared / Total Years &times; 40)</code><br>
        <span style="font-size: 0.82rem; color: #475569;">
            *Notice: These are historical preparation priorities to help allocate study time efficiently, not guaranteed predictions of future questions.
        </span>
    </div>
    """, unsafe_allow_html=True)

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    subj_filter = st.selectbox("Filter by Subject", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="it_subj")

    questions = db.get_questions(subject=subj_filter if subj_filter != "All Subjects" else None)
    kpis = db.get_kpis(subject=subj_filter if subj_filter != "All Subjects" else None)

    if not questions:
        st.info("No questions available for prioritization. Please upload past question papers.")
        return

    analyzer = TopicAnalyzer(questions)
    freq_summary = analyzer.get_topic_frequency_summary(exclude_unclassified=True)
    total_years = kpis.get("total_years", 1)

    priorities_df = PriorityPredictor.calculate_priorities(
        freq_summary_df=freq_summary,
        total_years=total_years,
        all_questions=questions
    )

    if priorities_df.empty:
        st.info("No classified topics available to calculate priority rankings.")
        return

    fig_prio = create_priority_distribution_chart(priorities_df)
    st.plotly_chart(fig_prio, use_container_width=True)

    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        prio_categories = ["All Categories", "Very High Priority", "High Priority", "Medium Priority", "Low Priority"]
        selected_cat = st.selectbox("Filter by Priority Tier", options=prio_categories, index=0, key="it_cat")

    filtered_prio = priorities_df
    if selected_cat != "All Categories":
        filtered_prio = priorities_df[priorities_df["Priority Category"] == selected_cat]

    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("Prioritized Topic Cards & Associated Exam Questions", "Explore why topics were ranked and review past questions", "📑")

    for _, row in filtered_prio.iterrows():
        topic_name = row["Topic"]
        badge_html = get_priority_badge_html(row["Priority Category"])

        with st.expander(f"**{topic_name}** — Score: {row['Priority Score']}/100 — {row['Frequency']} Questions across {row['Years Appeared']} Years"):
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                st.markdown(f"### Priority Status: {badge_html}", unsafe_allow_html=True)
                st.markdown(f"**Recommended Preparation:** {row['Preparation Advice']}")
                st.markdown(f"**Curriculum Unit:** `{row['Unit']}` | **Exam Coverage:** `{row['Years Appeared']} of {total_years} years`")
            with col_t2:
                st.metric("Priority Score", f"{row['Priority Score']} / 100")
                st.metric("Total Questions", f"{row['Frequency']}")

            related_qs = PriorityPredictor.get_related_questions_for_topic(topic_name, questions, limit=4)
            if related_qs:
                st.markdown("#### 📜 Representative Previous-Year Questions:")
                for rq in related_qs:
                    marks_str = f"[{rq['marks']} Marks]" if rq.get("marks") else ""
                    st.markdown(f"- **{rq['academic_year']} ({rq['question_number']})**: {rq['question_text']} *{marks_str}*")
            else:
                st.write("No specific questions linked.")

if __name__ == "__main__" or True:
    render()
