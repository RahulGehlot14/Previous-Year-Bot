"""
Unit tests for AI Study Planner module.
"""

import pytest
from datetime import date, timedelta
import pandas as pd
from modules.study_planner import StudyPlanner

def test_study_plan_generation():
    priorities_df = pd.DataFrame([
        {"Topic": "Database Normalization", "Unit": "Unit 2", "Priority Category": "Very High Priority", "Priority Score": 95.0},
        {"Topic": "SQL Queries", "Unit": "Unit 2", "Priority Category": "High Priority", "Priority Score": 80.0},
        {"Topic": "Indexing", "Unit": "Unit 3", "Priority Category": "Medium Priority", "Priority Score": 50.0},
    ])

    today = date.today()
    exam_date = today + timedelta(days=10)

    plan = StudyPlanner.generate_plan(priorities_df, exam_date, today, daily_hours=3.0)

    assert plan["total_days"] == 10
    assert len(plan["days"]) == 10
    assert plan["total_study_hours"] == 30.0

    # Ensure the first study topic is the highest priority topic
    first_day = plan["days"][0]
    assert first_day["topic"] == "Database Normalization"

    # Ensure mock exam is scheduled in the plan
    mock_days = [d for d in plan["days"] if d["type"] == "Mock Exam"]
    assert len(mock_days) >= 1
