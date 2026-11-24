"""
Interactive Data Visualizations for Previous Year Question Paper Analyzer.
Generates polished Plotly figures: Top Topics horizontal bar chart, topic distribution pie,
year-wise line charts, cross-year grouped bars, topic-year heatmap, and unit-wise stacked bars.
"""

from typing import Optional, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Consistent color palettes
PRIMARY_PALETTE = ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
PRIORITY_COLORS = {
    "Very High Priority": "#DC2626",
    "High Priority": "#EA580C",
    "Medium Priority": "#EAB308",
    "Low Priority": "#64748B"
}

def create_top_topics_bar_chart(df_summary: pd.DataFrame, n: int = 10) -> go.Figure:
    """1. Horizontal Bar Chart: Top N frequently asked topics."""
    if df_summary.empty:
        return _create_empty_figure("No topic data available")

    top_df = df_summary.head(n).iloc[::-1]  # Reverse for ascending horizontal display

    fig = px.bar(
        top_df,
        x="Frequency",
        y="Topic",
        orientation="h",
        text="Frequency",
        color="Frequency",
        color_continuous_scale="Blues",
        labels={"Frequency": "Total Questions Asked", "Topic": "Curriculum Topic"},
        title=f"Top {min(n, len(top_df))} Most Repeated Examination Topics"
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Questions: %{x}<br>Years Appeared: %{customdata[0]}<extra></extra>",
        customdata=top_df[["Years Appeared"]] if "Years Appeared" in top_df.columns else None
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=40, t=50, b=20),
        height=max(380, len(top_df) * 36),
        coloraxis_showscale=False
    )
    return fig

def create_topic_pie_chart(df_summary: pd.DataFrame, max_slices: int = 8) -> go.Figure:
    """2. Donut/Pie Chart: Overall topic distribution."""
    if df_summary.empty:
        return _create_empty_figure("No topic distribution data available")

    df_copy = df_summary.copy()
    if len(df_copy) > max_slices:
        top_slice = df_copy.head(max_slices - 1)
        others_count = df_copy.iloc[max_slices - 1:]["Frequency"].sum()
        others_row = pd.DataFrame([{
            "Topic": "Other Topics",
            "Frequency": others_count
        }])
        plot_df = pd.concat([top_slice, others_row], ignore_index=True)
    else:
        plot_df = df_copy

    fig = px.pie(
        plot_df,
        names="Topic",
        values="Frequency",
        hole=0.45,
        title="Curriculum Topic Distribution",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Questions: %{value} (%{percent})<extra></extra>"
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_year_wise_line_chart(df_questions: pd.DataFrame, top_topics: Optional[List[str]] = None) -> go.Figure:
    """3. Line Chart: Year-wise question frequency trend across academic years."""
    if df_questions.empty:
        return _create_empty_figure("No year-wise question data available")

    df = df_questions[df_questions["topic"] != "Unclassified"].copy()
    if df.empty:
        return _create_empty_figure("No classified questions for trend line")

    if top_topics:
        df = df[df["topic"].isin(top_topics)]
    else:
        # Default top 5 topics
        top_5 = df["topic"].value_counts().head(5).index.tolist()
        df = df[df["topic"].isin(top_5)]

    grouped = df.groupby(["academic_year", "topic"]).size().reset_index(name="Question Count")
    grouped.sort_values(by="academic_year", inplace=True)

    fig = px.line(
        grouped,
        x="academic_year",
        y="Question Count",
        color="topic",
        markers=True,
        title="Year-wise Trend of Prominent Topics",
        labels={"academic_year": "Academic Year", "Question Count": "Number of Questions", "topic": "Topic"}
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    return fig

def create_grouped_bar_chart(df_questions: pd.DataFrame, top_topics: Optional[List[str]] = None) -> go.Figure:
    """4. Grouped Bar Chart: Compare topics across academic years."""
    if df_questions.empty:
        return _create_empty_figure("No question data available for comparison")

    df = df_questions[df_questions["topic"] != "Unclassified"].copy()
    if top_topics:
        df = df[df["topic"].isin(top_topics)]
    else:
        top_5 = df["topic"].value_counts().head(5).index.tolist()
        df = df[df["topic"].isin(top_5)]

    grouped = df.groupby(["topic", "academic_year"]).size().reset_index(name="Count")

    fig = px.bar(
        grouped,
        x="topic",
        y="Count",
        color="academic_year",
        barmode="group",
        title="Topic Comparison Across Academic Years",
        labels={"topic": "Topic", "Count": "Question Count", "academic_year": "Year"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    return fig

def create_topic_year_heatmap(df_questions: pd.DataFrame, n_topics: int = 12) -> go.Figure:
    """5. Heatmap: Topics versus Academic Years frequency matrix."""
    if df_questions.empty:
        return _create_empty_figure("No data for heatmap matrix")

    df = df_questions[df_questions["topic"] != "Unclassified"].copy()
    if df.empty:
        return _create_empty_figure("No classified topics available")

    top_topics_list = df["topic"].value_counts().head(n_topics).index.tolist()
    filtered = df[df["topic"].isin(top_topics_list)]

    cross_tab = pd.crosstab(filtered["topic"], filtered["academic_year"])

    fig = px.imshow(
        cross_tab,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="YlGnBu",
        title="Topic Frequency Heatmap by Academic Year",
        labels=dict(x="Academic Year", y="Topic", color="Count")
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(360, len(cross_tab) * 32)
    )
    return fig

def create_unit_stacked_bar_chart(df_questions: pd.DataFrame) -> go.Figure:
    """6. Stacked Bar Chart: Unit-wise question distribution by difficulty."""
    if df_questions.empty:
        return _create_empty_figure("No unit distribution data available")

    df = df_questions.copy()
    grouped = df.groupby(["unit", "difficulty"]).size().reset_index(name="Question Count")

    fig = px.bar(
        grouped,
        x="unit",
        y="Question Count",
        color="difficulty",
        title="Unit-wise Question Distribution by Difficulty",
        labels={"unit": "Syllabus Unit", "Question Count": "Questions", "difficulty": "Difficulty"},
        color_discrete_map={"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}
    )
    fig.update_layout(
        template="plotly_white",
        barmode="stack",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_priority_distribution_chart(df_priorities: pd.DataFrame) -> go.Figure:
    """Renders priority score bar chart grouped by priority categories."""
    if df_priorities.empty:
        return _create_empty_figure("No priority data available")

    fig = px.bar(
        df_priorities.head(15),
        x="Priority Score",
        y="Topic",
        color="Priority Category",
        orientation="h",
        title="Topic Priority Score Ranking (Historical Yield)",
        color_discrete_map=PRIORITY_COLORS,
        text="Priority Score"
    )
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(380, len(df_priorities.head(15)) * 32)
    )
    return fig

def _create_empty_figure(message: str) -> go.Figure:
    """Creates a placeholder figure when dataset has no records."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#94A3B8")
    )
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=30, b=10),
        height=260
    )
    return fig
