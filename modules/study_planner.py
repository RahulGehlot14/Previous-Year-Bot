"""
AI Study Planner Module for Previous Year Question Paper Analyzer.
Generates structured, weighted day-by-day examination revision roadmaps
based on topic priority scores, available days, and daily study capacity.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class StudyPlanner:
    """Creates optimal, priority-weighted revision schedules for exam preparation."""

    @classmethod
    def generate_plan(cls, priorities_df: pd.DataFrame,
                      exam_date: datetime.date,
                      start_date: datetime.date,
                      daily_hours: float = 3.0) -> Dict[str, Any]:
        """
        Generates a balanced revision roadmap:
        - Allocates days proportionally to Priority Scores.
        - Schedules high-yield core topics first.
        - Injects spaced revision and mock test practice days near the end.
        """
        if priorities_df.empty:
            return {"days": [], "total_days": 0, "summary": "No topics available"}

        total_days = max(1, (exam_date - start_date).days)
        valid_topics = priorities_df[priorities_df["Topic"] != "Unclassified"].copy()

        if valid_topics.empty:
            valid_topics = priorities_df.copy()

        # Reserve last 1-3 days for comprehensive revision & mock exam practice
        prep_days = max(1, total_days - (2 if total_days >= 7 else 1))

        # Weight topic study time by Priority Score
        total_prio = valid_topics["Priority Score"].sum()
        if total_prio <= 0:
            total_prio = 1

        valid_topics["weight"] = valid_topics["Priority Score"] / total_prio
        valid_topics["raw_days"] = valid_topics["weight"] * prep_days

        # Ensure every high priority topic gets at least 1 day
        allocated_schedule = []
        current_date = start_date

        topic_list = valid_topics.to_dict(orient="records")

        # Distribute topics across available prep days
        day_idx = 1
        for t in topic_list:
            if day_idx > prep_days:
                break

            target_hours = round(daily_hours * max(1.0, float(t["weight"]) * prep_days), 1)
            allocated_schedule.append({
                "day_number": day_idx,
                "date": current_date.strftime("%b %d, %Y (%a)"),
                "topic": t["Topic"],
                "unit": t["Unit"],
                "priority_category": t["Priority Category"],
                "priority_score": t["Priority Score"],
                "target_hours": target_hours,
                "task": f"Deep dive into {t['Topic']}. Practice past exam questions, definitions, and key formulas.",
                "type": "Study"
            })
            current_date += timedelta(days=1)
            day_idx += 1

        # Fill remaining prep days if any
        while day_idx <= prep_days and topic_list:
            t = topic_list[(day_idx - 1) % len(topic_list)]
            allocated_schedule.append({
                "day_number": day_idx,
                "date": current_date.strftime("%b %d, %Y (%a)"),
                "topic": f"{t['Topic']} (Reinforcement)",
                "unit": t["Unit"],
                "priority_category": t["Priority Category"],
                "priority_score": t["Priority Score"],
                "target_hours": daily_hours,
                "task": f"Solve numericals and review diagrams for {t['Topic']}.",
                "type": "Practice"
            })
            current_date += timedelta(days=1)
            day_idx += 1

        # Add Full Mock Examination & Final Revision Days
        if total_days >= 3:
            allocated_schedule.append({
                "day_number": day_idx,
                "date": current_date.strftime("%b %d, %Y (%a)"),
                "topic": "Full Mock Exam Simulation",
                "unit": "All Units",
                "priority_category": "Very High Priority",
                "priority_score": 100.0,
                "target_hours": daily_hours,
                "task": "Attempt a timed 3-hour practice examination paper under test conditions. Review mistakes.",
                "type": "Mock Exam"
            })
            current_date += timedelta(days=1)
            day_idx += 1

        while day_idx <= total_days:
            allocated_schedule.append({
                "day_number": day_idx,
                "date": current_date.strftime("%b %d, %Y (%a)"),
                "topic": "Final High-Yield Review & Formula Memorization",
                "unit": "All Units",
                "priority_category": "High Priority",
                "priority_score": 90.0,
                "target_hours": daily_hours,
                "task": "Review flashcards, core definitions, Bloom Level remember/understand notes, and get adequate rest.",
                "type": "Final Revision"
            })
            current_date += timedelta(days=1)
            day_idx += 1

        return {
            "days": allocated_schedule,
            "total_days": total_days,
            "exam_date": exam_date.strftime("%B %d, %Y"),
            "daily_hours": daily_hours,
            "total_study_hours": round(total_days * daily_hours, 1)
        }
