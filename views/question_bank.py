"""
Question Bank View for Previous Year Question Paper Analyzer.
Provides full keyword search, multi-faceted filtering, original question inspection,
inline editing, deletion, and interactive Flashcard revision mode.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from utils.styling import render_section_header, render_flashcard, load_custom_css
from config import BLOOM_LEVELS, DIFFICULTY_LEVELS, QUESTION_TYPES

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Question Bank & Flashcard Mode", "Search, filter, view, edit, or practice with interactive revision flashcards", "🗃️")

    tab_search, tab_flashcards = st.tabs(["🔍 Searchable Repository", "🗂️ Interactive Flashcard Revision"])

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    all_years = ["All Years"] + db.get_all_years(subject=selected_subject)
    all_topics = ["All Topics"] + db.get_all_topics(subject=selected_subject)
    all_units = ["All Units"] + db.get_all_units(subject=selected_subject)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        subj_filter = st.selectbox("Subject", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="qb_subj_v")
    with col2:
        year_filter = st.selectbox("Academic Year", options=all_years, index=0, key="qb_yr_v")
    with col3:
        topic_filter = st.selectbox("Topic", options=all_topics, index=0, key="qb_top_v")
    with col4:
        unit_filter = st.selectbox("Unit", options=all_units, index=0, key="qb_unit_v")

    # Tab 1: Searchable List
    with tab_search:
        search_term = st.text_input("🔍 Full-text search (keywords, phrases, concepts)", placeholder="e.g. Explain relational model, calculate functional dependency, deadlock...")

        questions = db.get_questions(
            subject=subj_filter if subj_filter != "All Subjects" else None,
            topic=topic_filter if topic_filter != "All Topics" else None,
            unit=unit_filter if unit_filter != "All Units" else None,
            academic_year=year_filter if year_filter != "All Years" else None,
            search_query=search_term
        )

        st.markdown(f"**Found {len(questions)} questions matching your criteria:**")

        if not questions:
            st.info("No questions found matching your search. Please adjust your filters.")
        else:
            for q in questions:
                with st.expander(f"**{q['question_number']}** [{q['academic_year']}] — **{q['topic']}** — {q['subject']}"):
                    st.markdown(f"### Question:\n{q['question_text']}")

                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**Unit:** `{q['unit']}`")
                    c2.markdown(f"**Marks:** `{q.get('marks', 'Not specified')}`")
                    c3.markdown(f"**Difficulty:** `{q['difficulty']}`")
                    c4.markdown(f"**Bloom Level:** `{q['bloom_level']}`")

                    if q.get("subtopic"):
                        st.markdown(f"**Subtopic:** {q['subtopic']}")

                    if q.get("keywords"):
                        kw_str = ", ".join(q["keywords"]) if isinstance(q["keywords"], list) else str(q["keywords"])
                        st.markdown(f"**Keywords:** `{kw_str}`")

                    st.caption(f"Source Document: {q['source_document']} | Classification: {q['classification_source']}")

                    st.markdown("---")
                    act_col1, act_col2 = st.columns([4, 1])

                    with act_col2:
                        if st.button("🗑️ Delete", key=f"btn_del_q_{q['id']}", type="secondary"):
                            db.delete_question(q["id"])
                            st.success("Question deleted.")
                            st.rerun()

                    with act_col1:
                        with st.expander("✏️ Quick Edit Question Details"):
                            with st.form(key=f"quick_edit_form_{q['id']}"):
                                f_col1, f_col2 = st.columns(2)
                                with f_col1:
                                    e_topic = st.text_input("Topic", value=q["topic"])
                                    e_unit = st.text_input("Unit", value=q["unit"])
                                with f_col2:
                                    e_diff = st.selectbox("Difficulty", options=DIFFICULTY_LEVELS, index=DIFFICULTY_LEVELS.index(q["difficulty"]) if q["difficulty"] in DIFFICULTY_LEVELS else 1)
                                    e_marks = st.number_input("Marks", min_value=0.0, max_value=100.0, value=float(q["marks"]) if q["marks"] is not None else 0.0)

                                e_text = st.text_area("Question Text", value=q["question_text"])

                                if st.form_submit_button("Update Record"):
                                    db.update_question(q["id"], {
                                        "topic": e_topic.strip() or "Unclassified",
                                        "unit": e_unit.strip() or "General",
                                        "difficulty": e_diff,
                                        "marks": e_marks if e_marks > 0 else None,
                                        "question_text": e_text.strip(),
                                        "classification_source": "manual"
                                    })
                                    st.success("Updated successfully.")
                                    st.rerun()

    # Tab 2: Flashcard Mode
    with tab_flashcards:
        render_section_header("Active Recall Flashcard Mode", "Practice answering questions without looking at classifications", "🧠")

        fc_questions = db.get_questions(
            subject=subj_filter if subj_filter != "All Subjects" else None,
            topic=topic_filter if topic_filter != "All Topics" else None,
            unit=unit_filter if unit_filter != "All Units" else None,
            academic_year=year_filter if year_filter != "All Years" else None
        )

        if not fc_questions:
            st.info("No questions match the selected filters.")
        else:
            if "fc_index" not in st.session_state:
                st.session_state["fc_index"] = 0

            st.session_state["fc_index"] = max(0, min(st.session_state["fc_index"], len(fc_questions) - 1))
            current_q = fc_questions[st.session_state["fc_index"]]

            st.caption(f"Card {st.session_state['fc_index'] + 1} of {len(fc_questions)}")
            render_flashcard(current_q)

            col_prev, col_flip, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("⬅️ Previous Card", key="btn_prev_fc", use_container_width=True):
                    st.session_state["fc_index"] = max(0, st.session_state["fc_index"] - 1)
                    st.rerun()

            with col_next:
                if st.button("Next Card ➡️", key="btn_next_fc", use_container_width=True):
                    st.session_state["fc_index"] = min(len(fc_questions) - 1, st.session_state["fc_index"] + 1)
                    st.rerun()

if __name__ == "__main__" or True:
    render()
