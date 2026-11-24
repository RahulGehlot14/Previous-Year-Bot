"""
Topic Frequency Analyzer Module for Previous Year Question Paper Analyzer.
Uses Pandas to calculate topic frequencies, year appearances, paper distributions,
percentages, and comparative matrices.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

class TopicAnalyzer:
    """Performs statistical aggregation and frequency analysis on classified questions."""

    def __init__(self, questions: List[Dict[str, Any]]):
        self.raw_questions = questions
        self.df = self._build_dataframe(questions)

    def _build_dataframe(self, questions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts raw questions list to structured Pandas DataFrame with cleaned columns."""
        if not questions:
            return pd.DataFrame(columns=[
                "id", "question_id", "question_number", "question_text", "marks",
                "subject", "academic_year", "source_document", "unit", "topic",
                "subtopic", "keywords", "question_type", "difficulty", "bloom_level"
            ])

        df = pd.DataFrame(questions)
        # Ensure default values for missing columns
        for col in ["topic", "unit", "subject", "academic_year", "difficulty", "question_type", "bloom_level"]:
            if col not in df.columns:
                df[col] = "General" if col == "unit" else "Unclassified"
            else:
                df[col] = df[col].fillna("Unclassified" if col == "topic" else "General")

        if "marks" in df.columns:
            df["marks"] = pd.to_numeric(df["marks"], errors="coerce")

        return df

    def get_topic_frequency_summary(self, exclude_unclassified: bool = False) -> pd.DataFrame:
        """
        Calculates:
        - Topic
        - Unit
        - Frequency (total questions on this topic)
        - Years Appeared (distinct academic years)
        - Papers Count (distinct source documents/papers)
        - Topic Frequency Percentage
        - Avg Marks
        """
        if self.df.empty:
            return pd.DataFrame(columns=[
                "Topic", "Unit", "Frequency", "Years Appeared", "Papers Count", "Frequency %", "Avg Marks"
            ])

        df = self.df.copy()
        if exclude_unclassified:
            df = df[df["topic"] != "Unclassified"]

        if df.empty:
            return pd.DataFrame(columns=[
                "Topic", "Unit", "Frequency", "Years Appeared", "Papers Count", "Frequency %", "Avg Marks"
            ])

        total_questions = len(df)

        # Aggregate metrics per topic
        grouped = df.groupby("topic").agg(
            Unit=("unit", lambda x: x.mode().iloc[0] if not x.empty else "General"),
            Frequency=("id", "count"),
            Years_Appeared=("academic_year", lambda x: x.nunique()),
            Papers_Count=("source_document", lambda x: x.nunique()),
            Avg_Marks=("marks", lambda x: round(x.dropna().mean(), 1) if not x.dropna().empty else np.nan)
        ).reset_index()

        grouped.rename(columns={
            "topic": "Topic",
            "Years_Appeared": "Years Appeared",
            "Papers_Count": "Papers Count",
            "Avg_Marks": "Avg Marks"
        }, inplace=True)

        # Frequency percentage
        grouped["Frequency %"] = ((grouped["Frequency"] / total_questions) * 100).round(2)

        # Sort by frequency descending, then by years appeared
        grouped.sort_values(by=["Frequency", "Years Appeared"], ascending=[False, False], inplace=True)
        grouped.reset_index(drop=True, inplace=True)

        return grouped

    def get_year_wise_distribution(self, exclude_unclassified: bool = False) -> pd.DataFrame:
        """
        Generates pivot matrix: Topics vs Academic Years showing question counts.
        """
        if self.df.empty:
            return pd.DataFrame()

        df = self.df.copy()
        if exclude_unclassified:
            df = df[df["topic"] != "Unclassified"]

        if df.empty:
            return pd.DataFrame()

        pivot = pd.crosstab(
            index=df["topic"],
            columns=df["academic_year"],
            margins=True,
            margins_name="Total"
        )
        pivot.sort_values(by="Total", ascending=False, inplace=True)
        return pivot

    def get_unit_wise_summary(self) -> pd.DataFrame:
        """Aggregates question frequencies and unique topics by syllabus unit."""
        if self.df.empty:
            return pd.DataFrame(columns=["Unit", "Question Count", "Unique Topics", "Percentage"])

        grouped = self.df.groupby("unit").agg(
            Question_Count=("id", "count"),
            Unique_Topics=("topic", lambda x: x[x != "Unclassified"].nunique())
        ).reset_index()

        grouped.rename(columns={
            "unit": "Unit",
            "Question_Count": "Question Count",
            "Unique_Topics": "Unique Topics"
        }, inplace=True)

        total_q = len(self.df)
        grouped["Percentage"] = ((grouped["Question Count"] / total_q) * 100).round(2)
        grouped.sort_values(by="Question Count", ascending=False, inplace=True)
        return grouped

    def get_difficulty_summary(self) -> pd.DataFrame:
        """Returns question count breakdown across difficulty levels."""
        if self.df.empty:
            return pd.DataFrame()
        return self.df["difficulty"].value_counts().reset_index()

    def get_bloom_summary(self) -> pd.DataFrame:
        """Returns question count breakdown across Bloom's Taxonomy levels."""
        if self.df.empty:
            return pd.DataFrame()
        return self.df["bloom_level"].value_counts().reset_index()

    def get_top_topics(self, n: int = 10, exclude_unclassified: bool = True) -> pd.DataFrame:
        """Returns top N most frequently asked topics."""
        summary = self.get_topic_frequency_summary(exclude_unclassified=exclude_unclassified)
        return summary.head(n)

    def get_least_repeated_topics(self, n: int = 5) -> pd.DataFrame:
        """Returns least repeated topics (tail of the distribution)."""
        summary = self.get_topic_frequency_summary(exclude_unclassified=True)
        return summary.tail(n).sort_values(by="Frequency", ascending=True)
