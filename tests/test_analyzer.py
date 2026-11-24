"""
Automated unit tests for topic frequency calculation and priority scoring.
"""

import pytest
import pandas as pd
from modules.topic_analyzer import TopicAnalyzer
from modules.priority_predictor import PriorityPredictor

@pytest.fixture
def sample_questions_dataset():
    return [
        {"id": 1, "topic": "Database Normalization", "unit": "Unit 2", "academic_year": "2022", "marks": 10.0, "source_document": "p1.pdf"},
        {"id": 2, "topic": "Database Normalization", "unit": "Unit 2", "academic_year": "2023", "marks": 10.0, "source_document": "p2.pdf"},
        {"id": 3, "topic": "Database Normalization", "unit": "Unit 2", "academic_year": "2024", "marks": 10.0, "source_document": "p3.pdf"},
        {"id": 4, "topic": "SQL Queries & DDL/DML", "unit": "Unit 2", "academic_year": "2022", "marks": 5.0, "source_document": "p1.pdf"},
        {"id": 5, "topic": "SQL Queries & DDL/DML", "unit": "Unit 2", "academic_year": "2023", "marks": 5.0, "source_document": "p2.pdf"},
        {"id": 6, "topic": "Storage & Indexing", "unit": "Unit 3", "academic_year": "2024", "marks": 10.0, "source_document": "p3.pdf"},
    ]

def test_topic_frequency_aggregation(sample_questions_dataset):
    analyzer = TopicAnalyzer(sample_questions_dataset)
    summary = analyzer.get_topic_frequency_summary()

    assert not summary.empty
    norm_row = summary[summary["Topic"] == "Database Normalization"].iloc[0]
    assert norm_row["Frequency"] == 3
    assert norm_row["Years Appeared"] == 3
    assert norm_row["Papers Count"] == 3
    assert norm_row["Frequency %"] == 50.0  # 3 out of 6 questions

def test_priority_score_formula(sample_questions_dataset):
    analyzer = TopicAnalyzer(sample_questions_dataset)
    summary = analyzer.get_topic_frequency_summary()
    priorities = PriorityPredictor.calculate_priorities(summary, total_years=3)

    assert not priorities.empty
    top_prio = priorities.iloc[0]
    # Database Normalization has max frequency (3/3 * 60 = 60) and appeared in all 3 years (3/3 * 40 = 40)
    # Total priority score must be 100.0!
    assert top_prio["Topic"] == "Database Normalization"
    assert top_prio["Priority Score"] == 100.0
    assert top_prio["Priority Category"] == "Very High Priority"

def test_year_wise_distribution_matrix(sample_questions_dataset):
    analyzer = TopicAnalyzer(sample_questions_dataset)
    pivot = analyzer.get_year_wise_distribution()
    assert "2022" in pivot.columns
    assert "2023" in pivot.columns
    assert "2024" in pivot.columns
    assert pivot.loc["Database Normalization", "Total"] == 3
