"""
Unit tests for Question Similarity Engine.
"""

import pytest
from modules.similarity_engine import SimilarityEngine

def test_jaccard_similarity_calculation():
    text1 = "Explain 1NF, 2NF and 3NF with relational table examples."
    text2 = "Define 1NF, 2NF and 3NF with relational schema examples."
    sim = SimilarityEngine.calculate_similarity(text1, text2)
    assert sim >= 0.50

def test_dissimilar_questions():
    text1 = "Explain 1NF, 2NF and 3NF normalization."
    text2 = "What is CAP theorem in distributed NoSQL databases?"
    sim = SimilarityEngine.calculate_similarity(text1, text2)
    assert sim < 0.20

def test_find_cross_year_duplicates():
    questions = [
        {"id": 1, "question_number": "Q1", "academic_year": "2022", "question_text": "Explain ACID properties of transactions in detail.", "topic": "Transactions"},
        {"id": 2, "question_number": "Q3", "academic_year": "2024", "question_text": "Explain ACID properties of database transactions with bank examples.", "topic": "Transactions"},
        {"id": 3, "question_number": "Q2", "academic_year": "2023", "question_text": "Draw an ER diagram for a hospital management system.", "topic": "ER Model"},
    ]
    duplicates = SimilarityEngine.find_cross_year_duplicates(questions, threshold=0.30)
    assert len(duplicates) >= 1
    top_dup = duplicates[0]
    assert top_dup["q1_year"] != top_dup["q2_year"]
    assert top_dup["similarity_pct"] >= 30
