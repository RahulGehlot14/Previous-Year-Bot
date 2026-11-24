"""
Unit tests for Mock Exam Paper Generator.
"""

import pytest
from modules.mock_exam_generator import MockExamGenerator

def test_mock_paper_generation():
    questions = [
        {"id": 1, "question_text": "What is 1NF, 2NF and 3NF?", "unit": "Unit 2", "topic": "Normalization", "marks": 10.0, "bloom_level": "Understand"},
        {"id": 2, "question_text": "Explain ER diagrams.", "unit": "Unit 1", "topic": "ER Model", "marks": 10.0, "bloom_level": "Understand"},
        {"id": 3, "question_text": "Write SQL queries for join.", "unit": "Unit 2", "topic": "SQL", "marks": 10.0, "bloom_level": "Apply"},
        {"id": 4, "question_text": "Explain ACID properties.", "unit": "Unit 3", "topic": "Transactions", "marks": 10.0, "bloom_level": "Understand"},
        {"id": 5, "question_text": "What is a B+ tree?", "unit": "Unit 4", "topic": "Indexing", "marks": 10.0, "bloom_level": "Remember"},
        {"id": 6, "question_text": "Explain CAP theorem.", "unit": "Unit 5", "topic": "NoSQL", "marks": 10.0, "bloom_level": "Analyze"},
    ]

    mock = MockExamGenerator.generate_mock_paper(questions, subject="DBMS", total_marks=50, duration_hours=2)

    assert "MOCK EXAMINATION - DBMS" in mock["title"]
    assert mock["duration"] == "2 Hours"
    assert len(mock["questions"]) >= 5
    assert mock["total_marks"] >= 50
    # Each question should have a mock question number like Q1, Q2
    assert mock["questions"][0]["mock_question_number"] == "Q1"
