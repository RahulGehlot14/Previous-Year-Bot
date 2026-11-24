"""
Question Analysis View for Previous Year Question Paper Analyzer.
Enables fine-grained inspection, multi-dimensional filtering,
and inline topic classification editing.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from utils.styling import render_section_header, load_custom_css
from config import BLOOM_LEVELS, DIFFICULTY_LEVELS, QUESTION_TYPES

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Question Analysis", "Inspect, filter, and manually calibrate extracted questions and AI topic classifications", "🔎")

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    all_years = ["All Years"] + db.get_all_years(subject=selected_subject)
    all_topics = ["All Topics"] + db.get_all_topics(subject=selected_subject)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        subj_filter = st.selectbox("Subject Filter", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="qa_subj")
    with col2:
        year_filter = st.selectbox("Academic Year", options=all_years, index=0, key="qa_yr")
    with col3:
        topic_filter = st.selectbox("Topic", options=all_topics, index=0, key="qa_top")
    with col4:
        diff_filter = st.selectbox("Difficulty", options=["All Difficulties"] + DIFFICULTY_LEVELS, index=0, key="qa_diff")

    search_kw = st.text_input("🔍 Search question text, subtopics, or keywords", placeholder="e.g. Normalization, B-Tree, ACID, Deadlock...")

    questions = db.get_questions(
        subject=subj_filter if subj_filter != "All Subjects" else None,
        topic=topic_filter if topic_filter != "All Topics" else None,
        academic_year=year_filter if year_filter != "All Years" else None,
        difficulty=diff_filter if diff_filter != "All Difficulties" else None,
        search_query=search_kw
    )

    st.markdown(f"**Showing {len(questions)} matching questions:**")

    if not questions:
        st.info("No questions match the current filter criteria. Try broadening your filters.")
        return

    for idx, q in enumerate(questions):
        with st.expander(
            f"**{q['question_number']}** [{q['academic_year']}] — **{q['topic']}** ({q.get('marks', 'N/A')} Marks) — *{q['difficulty']}*",
            expanded=(idx < 2)
        ):
            st.markdown(f"### Question Text\n> {q['question_text']}")

            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**Unit:** `{q['unit']}`")
            c2.markdown(f"**Type:** `{q['question_type']}`")
            c3.markdown(f"**Bloom's Level:** `{q['bloom_level']}`")
            c4.markdown(f"**Source Document:** `{q['source_document']}`")

            if q.get("keywords"):
                kw_str = ", ".join(q["keywords"]) if isinstance(q["keywords"], list) else str(q["keywords"])
                st.markdown(f"**Keywords:** `{kw_str}`")

            st.caption(f"Classification Source: {q.get('classification_source', 'rule_based')}")

            # Edit Form
            st.markdown("---")
            with st.form(key=f"edit_q_form_{q['id']}"):
                st.markdown("#### ✏️ Edit or Correct Topic Classification")
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    new_topic = st.text_input("Topic Name", value=q["topic"])
                    new_unit = st.text_input("Syllabus Unit", value=q["unit"])
                    new_subtopic = st.text_input("Subtopic", value=q.get("subtopic", ""))
                with e_col2:
                    new_diff = st.selectbox("Difficulty", options=DIFFICULTY_LEVELS, index=DIFFICULTY_LEVELS.index(q["difficulty"]) if q["difficulty"] in DIFFICULTY_LEVELS else 1)
                    new_bloom = st.selectbox("Bloom's Level", options=BLOOM_LEVELS, index=BLOOM_LEVELS.index(q["bloom_level"]) if q["bloom_level"] in BLOOM_LEVELS else 1)
                    new_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=float(q["marks"]) if q["marks"] is not None else 0.0)

                new_q_text = st.text_area("Question Text", value=q["question_text"], height=80)

                submitted = st.form_submit_button("💾 Save Changes", type="primary")
                if submitted:
                    updates = {
                        "topic": new_topic.strip() or "Unclassified",
                        "unit": new_unit.strip() or "General",
                        "subtopic": new_subtopic.strip(),
                        "difficulty": new_diff,
                        "bloom_level": new_bloom,
                        "marks": new_marks if new_marks > 0 else None,
                        "question_text": new_q_text.strip(),
                        "classification_source": "manual"
                    }
                    db.update_question(q["id"], updates)
                    st.success("Question classification updated successfully!")
                    st.rerun()

if __name__ == "__main__" or True:
    render()
