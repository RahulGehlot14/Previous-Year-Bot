"""
Topic Frequency View for Previous Year Question Paper Analyzer.
Presents detailed topic frequency distributions, percentages, rankings,
side-by-side topic comparison, and multi-angle charts.
"""

import streamlit as st
import pandas as pd
from database.db_manager import DatabaseManager
from modules.topic_analyzer import TopicAnalyzer
from modules.visualization import (
    create_top_topics_bar_chart,
    create_topic_pie_chart,
    create_unit_stacked_bar_chart
)
from utils.styling import render_section_header, load_custom_css

def render():
    load_custom_css()

    if "db_manager" not in st.session_state:
        st.session_state["db_manager"] = DatabaseManager()
    db: DatabaseManager = st.session_state["db_manager"]

    selected_subject = st.session_state.get("active_subject", "All Subjects")

    render_section_header("Topic Frequency Analysis", "Statistical ranking, recurrence frequency, and side-by-side topic comparisons", "📊")

    all_subjects = ["All Subjects"] + db.get_all_subjects()
    subj_filter = st.selectbox("Select Subject", options=all_subjects, index=all_subjects.index(selected_subject) if selected_subject in all_subjects else 0, key="tf_subj")

    questions = db.get_questions(subject=subj_filter if subj_filter != "All Subjects" else None)

    if not questions:
        st.info("No questions found for the selected subject. Upload papers to begin analysis.")
        return

    analyzer = TopicAnalyzer(questions)
    freq_summary = analyzer.get_topic_frequency_summary(exclude_unclassified=False)

    if freq_summary.empty:
        st.info("No topics classified yet.")
        return

    tab_overview, tab_compare = st.tabs(["📈 Frequency Overview & Charts", "⚖️ Side-by-Side Topic Comparator"])

    with tab_overview:
        col_chart1, col_chart2 = st.columns([3, 2])
        with col_chart1:
            fig_bar = create_top_topics_bar_chart(freq_summary, n=10)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            fig_pie = create_topic_pie_chart(freq_summary, max_slices=8)
            st.plotly_chart(fig_pie, use_container_width=True)

        render_section_header("Unit-wise Breakdown", "Distribution of questions across syllabus units and difficulty levels", "📚")
        q_df = pd.DataFrame(questions)
        fig_unit = create_unit_stacked_bar_chart(q_df)
        st.plotly_chart(fig_unit, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("Complete Topic Frequency Table", "Ranked from most to least frequently repeated topic", "📋")

        st.dataframe(
            freq_summary,
            column_config={
                "Frequency %": st.column_config.ProgressColumn(
                    "Curriculum Share",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "Frequency": st.column_config.NumberColumn("Total Questions"),
                "Years Appeared": st.column_config.NumberColumn("Exam Years"),
                "Papers Count": st.column_config.NumberColumn("Papers Count"),
                "Avg Marks": st.column_config.NumberColumn("Avg Marks", format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_most, col_least = st.columns(2)

        with col_most:
            st.markdown("### 🔥 Top 5 Most Repeated Topics")
            top_5 = analyzer.get_top_topics(n=5)
            for _, row in top_5.iterrows():
                st.markdown(f"- **{row['Topic']}** — {row['Frequency']} questions across {row['Years Appeared']} years ({row['Frequency %']}%)")

        with col_least:
            st.markdown("### ❄️ Least Repeated Topics")
            least_5 = analyzer.get_least_repeated_topics(n=5)
            for _, row in least_5.iterrows():
                st.markdown(f"- **{row['Topic']}** — {row['Frequency']} questions across {row['Years Appeared']} years ({row['Frequency %']}%)")

    with tab_compare:
        render_section_header("Compare Topics Directly", "Select 2 or more topics to analyze differences in coverage and appearance", "🔍")
        all_topic_names = freq_summary["Topic"].tolist()
        selected_topics = st.multiselect(
            "Select topics to compare",
            options=all_topic_names,
            default=all_topic_names[:3] if len(all_topic_names) >= 3 else all_topic_names
        )

        if selected_topics:
            comp_df = freq_summary[freq_summary["Topic"].isin(selected_topics)]
            st.dataframe(comp_df, hide_index=True, use_container_width=True)

            import plotly.express as px
            fig_comp = px.bar(
                comp_df,
                x="Topic",
                y="Frequency",
                color="Topic",
                text="Frequency",
                title="Direct Topic Frequency Comparison",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_comp.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Select at least one topic above to compare.")

if __name__ == "__main__" or True:
    render()
