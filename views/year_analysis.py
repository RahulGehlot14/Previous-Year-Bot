"""
Year-wise Analysis View for Previous Year Question Paper Analyzer.
Examines multi-year trends, question frequency evolutions, heatmaps, and cross-year topic comparisons.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.visualization import (
    create_year_wise_line_chart,
    create_grouped_bar_chart,
    create_topic_year_heatmap
)
from utils.styling import render_section_header, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Year-wise Analysis", "Observe curriculum topic patterns across consecutive examination cycles", "📅")

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    subj_filter = st.selectbox("Subject", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="ya_subj")

    questions = db.get_questions(subject=subj_filter if subj_filter != "All Subjects" else None)
    years = db.get_all_years(subject=subj_filter if subj_filter != "All Subjects" else None)

    if not questions or len(years) == 0:
        st.info("No multi-year examination data available for this subject. Upload papers from at least two different academic years.")
        return

    q_df = pd.DataFrame(questions)
    analyzer = TopicAnalyzer(questions)

    st.markdown(f"**Analyzed {len(questions)} questions across {len(years)} academic cycles:** `{', '.join(years)}`")

    render_section_header("Topic Frequency Heatmap", "Matrix showing question intensity for each topic by year", "🔥")
    fig_heatmap = create_topic_year_heatmap(q_df, n_topics=15)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    col_line, col_bar = st.columns(2)

    with col_line:
        render_section_header("Yearly Trajectory", "Line trend of top recurring topics", "📈")
        fig_line = create_year_wise_line_chart(q_df)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_bar:
        render_section_header("Cross-Year Comparison", "Grouped bars for direct annual comparison", "📊")
        fig_bar = create_grouped_bar_chart(q_df)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("Topic vs Academic Year Matrix", "Detailed numerical count of questions per topic in each exam year", "📋")
    pivot_df = analyzer.get_year_wise_distribution(exclude_unclassified=True)
    if not pivot_df.empty:
        st.dataframe(pivot_df, use_container_width=True)
    else:
        st.write("No cross-year data available.")

if __name__ == "__main__" or True:
    render()
