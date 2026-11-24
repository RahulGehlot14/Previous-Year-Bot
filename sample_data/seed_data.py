"""
Sample Data Seeder Module.
Preloads synthetic DBMS examination papers across 2022, 2023, and 2024 into SQLite.
"""

from pathlib import Path
from database.db_manager import DatabaseManager
from modules.document_processor import DocumentProcessor
from modules.question_extractor import QuestionExtractor
from modules.ai_classifier import AIClassifier
from utils.helpers import compute_file_hash
from config import SAMPLES_DIR

def seed_sample_database(db: DatabaseManager) -> int:
    """
    Reads synthetic DBMS exam papers, extracts questions, classifies them,
    and inserts them into SQLite. Returns total seeded questions count.
    """
    sample_files = [
        ("DBMS_PYQ_2022.txt", "2022"),
        ("DBMS_PYQ_2023.txt", "2023"),
        ("DBMS_PYQ_2024.txt", "2024")
    ]

    subject = "Database Management Systems (DBMS)"
    total_seeded = 0
    classifier = AIClassifier()

    for filename, year in sample_files:
        file_path = SAMPLES_DIR / filename
        if not file_path.exists():
            continue

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        f_hash = compute_file_hash(file_bytes)
        # Skip if already exists
        if db.paper_exists_by_hash(f_hash):
            continue

        # Extract text & questions
        text, _ = DocumentProcessor.extract_text(file_bytes, filename)
        questions = QuestionExtractor.extract_questions(
            text=text,
            filename=filename,
            subject=subject,
            academic_year=year
        )

        if not questions:
            continue

        # Insert paper record
        paper_id = db.insert_paper(
            filename=filename,
            file_hash=f_hash,
            file_size=len(file_bytes),
            file_type="txt",
            subject=subject,
            academic_year=year
        )

        for q in questions:
            q["paper_id"] = paper_id

        # Classify
        classified = classifier.classify_questions(questions)

        # Batch insert
        db.insert_questions_batch(classified)
        db.update_paper_question_count(paper_id, len(classified))
        total_seeded += len(classified)

    return total_seeded
