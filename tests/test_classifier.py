"""
Automated unit tests for AI and rule-based topic classification, Bloom's level, and JSON validation.
"""

import pytest
import json
from modules.ai_classifier import AIClassifier
from utils.helpers import safe_json_loads

def test_rule_based_normalization_classification():
    q = {
        "question_id": "Q001",
        "question_text": "Explain normalization in DBMS. What are 1NF, 2NF and 3NF? Eliminate redundancy with examples.",
        "subject": "DBMS",
        "academic_year": "2023",
        "marks": 10.0
    }
    res = AIClassifier.classify_rule_based(q)
    assert res["topic"] == "Database Normalization"
    assert res["unit"] == "Unit 2"
    assert "Normalization" in [k.title() for k in res["keywords"]]
    assert res["bloom_level"] == "Understand"
    assert res["difficulty"] == "Hard" or res["difficulty"] == "Medium"

def test_multi_year_topic_consistency():
    # Demonstrates that similar questions from different years map to the exact same topic name
    q_2022 = {
        "question_id": "Q01",
        "question_text": "Define 1NF, 2NF and 3NF with suitable relational table examples.",
        "subject": "DBMS",
        "academic_year": "2022"
    }
    q_2023 = {
        "question_id": "Q02",
        "question_text": "What is Database Normalization? How does normalization eliminate insertion and deletion anomalies?",
        "subject": "DBMS",
        "academic_year": "2023"
    }
    res_2022 = AIClassifier.classify_rule_based(q_2022)
    res_2023 = AIClassifier.classify_rule_based(q_2023)

    assert res_2022["topic"] == res_2023["topic"]
    assert res_2022["topic"] == "Database Normalization"

def test_transaction_concurrency_classification():
    q = {
        "question_id": "Q003",
        "question_text": "Explain Two-Phase Locking (2PL) protocol. How does strict 2PL avoid cascading aborts and deadlocks?",
        "subject": "DBMS",
        "academic_year": "2024",
        "marks": 10.0
    }
    res = AIClassifier.classify_rule_based(q)
    assert res["topic"] == "Transaction Management & Concurrency Control"
    assert res["unit"] == "Unit 4"

def test_safe_json_loads_markdown_fences():
    raw_json_in_markdown = """
    ```json
    [
      {
        "question_id": "Q001",
        "topic": "Storage & Indexing",
        "difficulty": "Medium"
      }
    ]
    ```
    """
    parsed = safe_json_loads(raw_json_in_markdown)
    assert isinstance(parsed, list)
    assert parsed[0]["question_id"] == "Q001"
    assert parsed[0]["topic"] == "Storage & Indexing"
