"""
Priority Predictor Module for Previous Year Question Paper Analyzer.
Calculates historical priority scores to help students prioritize high-yield topics
for examination preparation.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from config import (
    FREQUENCY_WEIGHT,
    YEARS_WEIGHT,
    PRIORITY_VERY_HIGH,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM
)

class PriorityPredictor:
    """
    Computes priority scores and categorizes topics for exam revision:
    Priority Score = (Topic Frequency / Max Topic Frequency * 60) + (Years Appeared / Total Years * 40)
    """

    @classmethod
    def calculate_priorities(cls, freq_summary_df: pd.DataFrame,
                             total_years: int,
                             all_questions: Optional[List[Dict[str, Any]]] = None) -> pd.DataFrame:
        """
        Takes topic frequency summary DataFrame and enriches it with:
        - Priority Score (0 to 100)
        - Priority Category (Very High, High, Medium, Low)
        - Study Advice / Exam Preparation Tips
        - Question Count
        """
        if freq_summary_df.empty:
            return pd.DataFrame(columns=[
                "Topic", "Unit", "Frequency", "Years Appeared", "Papers Count",
                "Frequency %", "Priority Score", "Priority Category", "Preparation Advice"
            ])

        df = freq_summary_df.copy()

        # Maximum frequency among identified topics
        max_freq = df["Frequency"].max() if not df.empty else 1
        if max_freq <= 0:
            max_freq = 1

        tot_years = max(1, total_years)

        # Transparent formula:
        # Score = (Frequency / Max Frequency * 60) + (Years Appeared / Total Years * 40)
        df["Priority Score"] = (
            ((df["Frequency"] / max_freq) * FREQUENCY_WEIGHT) +
            ((df["Years Appeared"] / tot_years) * YEARS_WEIGHT)
        ).round(1)

        # Ensure scores are clamped between 0 and 100
        df["Priority Score"] = df["Priority Score"].clip(0.0, 100.0)

        # Assign Priority Category
        def categorize(score: float) -> str:
            if score >= PRIORITY_VERY_HIGH:
                return "Very High Priority"
            elif score >= PRIORITY_HIGH:
                return "High Priority"
            elif score >= PRIORITY_MEDIUM:
                return "Medium Priority"
            return "Low Priority"

        def advice(category: str) -> str:
            if category == "Very High Priority":
                return "Core topic appearing consistently almost every year. Master definitions, proofs, numerical problems, and key diagrams thoroughly."
            elif category == "High Priority":
                return "Frequently repeated across multiple papers. High likelihood of substantial questions; ensure all fundamental concepts are covered."
            elif category == "Medium Priority":
                return "Moderately frequent topic. Review previous year patterns and solve at least 2-3 standard questions from this topic."
            return "Occasional or specialized topic. Cover basics after finishing Very High and High priority topics."

        df["Priority Category"] = df["Priority Score"].apply(categorize)
        df["Preparation Advice"] = df["Priority Category"].apply(advice)

        # Sort by priority score descending
        df.sort_values(by="Priority Score", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    @classmethod
    def get_related_questions_for_topic(cls, topic_name: str,
                                        questions: List[Dict[str, Any]],
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves representative past examination questions associated with a given topic."""
        matches = [q for q in questions if q.get("topic") == topic_name]
        # Sort by year descending to show newest questions first
        matches.sort(key=lambda x: str(x.get("academic_year", "")), reverse=True)
        return matches[:limit]
