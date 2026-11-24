"""
Automated unit tests for document processing and question extraction.
"""

import pytest
from modules.document_processor import DocumentProcessor
from modules.question_extractor import QuestionExtractor

SAMPLE_EXAM_TEXT = """
UNIVERSITY SEMESTER EXAMINATION - 2023
COURSE: B.Tech Computer Science
SUBJECT: DBMS
TIME: 3 Hours
MAX MARKS: 100

Q1. Explain the three-schema architecture of DBMS and discuss data independence. [10 Marks]

Q2. What is an ER Diagram? Draw an ER diagram for a library system. [10 Marks]

3. Define 1NF, 2NF, and 3NF with examples. (5)
a) What is Boyce-Codd Normal Form (BCNF)? [5 Marks]
b) Explain functional dependency preservation. [5 Marks]

Question 4. Explain ACID properties in transaction processing. [10 Marks]
"""

def test_question_extraction_counts():
    questions = QuestionExtractor.extract_questions(
        text=SAMPLE_EXAM_TEXT,
        filename="test_exam.txt",
        subject="DBMS",
        academic_year="2023"
    )
    # Should extract at least 4 primary questions / subquestions
    assert len(questions) >= 4
    numbers = [q["question_number"] for q in questions]
    assert any("Q1" in n or "1" in n for n in numbers)
    assert any("Q2" in n or "2" in n for n in numbers)

def test_marks_extraction():
    questions = QuestionExtractor.extract_questions(
        text=SAMPLE_EXAM_TEXT,
        filename="test_exam.txt",
        subject="DBMS",
        academic_year="2023"
    )
    first_q = questions[0]
    assert first_q["marks"] == 10.0

def test_clean_text_preserves_question_content():
    raw = "   Page 1 of 5\n\n\nQ1. Explain ACID properties.\n\n\n"
    questions = QuestionExtractor.extract_questions(raw, "doc.txt", "DBMS", "2023")
    assert len(questions) == 1
    assert "Explain ACID properties." in questions[0]["question_text"]

def test_empty_document_handling():
    with pytest.raises(ValueError, match="empty"):
        DocumentProcessor.extract_text(b"", "empty.txt")
