"""
Database Manager for Previous Year Question Paper Analyzer.
Handles SQLite database connection, table initialization, parameterized queries,
and CRUD operations for papers, questions, topics, and analysis results.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from config import DB_PATH, BASE_DIR

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

class DatabaseManager:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection with foreign keys enabled and row factory set to sqlite3.Row."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        """Initializes database schema if tables do not exist."""
        with self.get_connection() as conn:
            if SCHEMA_PATH.exists():
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            conn.commit()

    # ==========================
    # Papers Management
    # ==========================

    def paper_exists_by_hash(self, file_hash: str) -> bool:
        """Checks if a paper with identical content hash already exists."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT id FROM papers WHERE file_hash = ?", (file_hash,))
            return cur.fetchone() is not None

    def insert_paper(self, filename: str, file_hash: str, file_size: int,
                     file_type: str, subject: str, academic_year: str) -> int:
        """Inserts a new paper metadata record and returns its ID."""
        with self.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO papers (filename, file_hash, file_size, file_type, subject, academic_year, question_count, status)
                VALUES (?, ?, ?, ?, ?, ?, 0, 'processed')
                """,
                (filename, file_hash, file_size, file_type, subject, academic_year)
            )
            conn.commit()
            return cur.lastrowid

    def update_paper_question_count(self, paper_id: int, count: int):
        """Updates the question count for a paper."""
        with self.get_connection() as conn:
            conn.execute("UPDATE papers SET question_count = ? WHERE id = ?", (count, paper_id))
            conn.commit()

    def get_papers(self, subject: Optional[str] = None, academic_year: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves papers with optional filtering by subject and academic year."""
        query = "SELECT * FROM papers WHERE 1=1"
        params = []
        if subject and subject != "All Subjects":
            query += " AND subject = ?"
            params.append(subject)
        if academic_year and academic_year != "All Years":
            query += " AND academic_year = ?"
            params.append(academic_year)
        query += " ORDER BY uploaded_at DESC"

        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def delete_paper(self, paper_id: int) -> bool:
        """Deletes a paper and all associated extracted questions via cascading delete."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM questions WHERE paper_id = ?", (paper_id,))
            cur = conn.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
            conn.commit()
            return cur.rowcount > 0

    # ==========================
    # Questions Management
    # ==========================

    def insert_questions_batch(self, questions: List[Dict[str, Any]]) -> int:
        """Inserts a batch of extracted and classified questions."""
        if not questions:
            return 0
        
        insert_sql = """
        INSERT INTO questions (
            question_id, paper_id, question_number, question_text, marks,
            subject, academic_year, source_document, unit, topic, subtopic,
            keywords, question_type, difficulty, bloom_level, classification_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        records = []
        for q in questions:
            kw = q.get("keywords", [])
            kw_str = json.dumps(kw) if isinstance(kw, list) else str(kw)
            records.append((
                q.get("question_id", ""),
                q.get("paper_id"),
                q.get("question_number", ""),
                q.get("question_text", ""),
                q.get("marks"),
                q.get("subject", ""),
                q.get("academic_year", ""),
                q.get("source_document", ""),
                q.get("unit", "General"),
                q.get("topic", "Unclassified"),
                q.get("subtopic", ""),
                kw_str,
                q.get("question_type", "Theory"),
                q.get("difficulty", "Medium"),
                q.get("bloom_level", "Understand"),
                q.get("classification_source", "rule_based")
            ))

        with self.get_connection() as conn:
            conn.executemany(insert_sql, records)
            conn.commit()
            return len(records)

    def get_questions(self, subject: Optional[str] = None, topic: Optional[str] = None,
                      unit: Optional[str] = None, academic_year: Optional[str] = None,
                      difficulty: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves questions with multi-parameter filtering."""
        query = "SELECT * FROM questions WHERE 1=1"
        params = []

        if subject and subject != "All Subjects":
            query += " AND subject = ?"
            params.append(subject)
        if topic and topic != "All Topics":
            query += " AND topic = ?"
            params.append(topic)
        if unit and unit != "All Units":
            query += " AND unit = ?"
            params.append(unit)
        if academic_year and academic_year != "All Years":
            query += " AND academic_year = ?"
            params.append(academic_year)
        if difficulty and difficulty != "All Difficulties":
            query += " AND difficulty = ?"
            params.append(difficulty)
        if search_query and search_query.strip():
            query += " AND (question_text LIKE ? OR topic LIKE ? OR subtopic LIKE ? OR keywords LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term, term, term])

        query += " ORDER BY academic_year DESC, question_number ASC, id ASC"

        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            rows = [dict(row) for row in cur.fetchall()]
            # Parse keywords JSON
            for r in rows:
                try:
                    r["keywords"] = json.loads(r["keywords"]) if r.get("keywords") else []
                except Exception:
                    r["keywords"] = [r["keywords"]] if r.get("keywords") else []
            return rows

    def get_question_by_id(self, q_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single question by primary key ID."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT * FROM questions WHERE id = ?", (q_id,))
            row = cur.fetchone()
            if not row:
                return None
            res = dict(row)
            try:
                res["keywords"] = json.loads(res["keywords"]) if res.get("keywords") else []
            except Exception:
                res["keywords"] = []
            return res

    def update_question(self, q_id: int, updates: Dict[str, Any]) -> bool:
        """Updates fields of an existing question."""
        if not updates:
            return False
        
        allowed_cols = [
            "question_text", "question_number", "marks", "subject", "academic_year",
            "unit", "topic", "subtopic", "keywords", "question_type", "difficulty",
            "bloom_level", "classification_source"
        ]
        set_clauses = []
        params = []

        for k, v in updates.items():
            if k in allowed_cols:
                set_clauses.append(f"{k} = ?")
                if k == "keywords" and isinstance(v, list):
                    params.append(json.dumps(v))
                else:
                    params.append(v)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(q_id)
        sql = f"UPDATE questions SET {', '.join(set_clauses)} WHERE id = ?"

        with self.get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.rowcount > 0

    def delete_question(self, q_id: int) -> bool:
        """Deletes an individual question by ID."""
        with self.get_connection() as conn:
            # Check paper_id to decrement paper question count
            cur_paper = conn.execute("SELECT paper_id FROM questions WHERE id = ?", (q_id,))
            row = cur_paper.fetchone()
            cur = conn.execute("DELETE FROM questions WHERE id = ?", (q_id,))
            if row and row["paper_id"]:
                conn.execute(
                    "UPDATE papers SET question_count = (SELECT COUNT(*) FROM questions WHERE paper_id = ?) WHERE id = ?",
                    (row["paper_id"], row["paper_id"])
                )
            conn.commit()
            return cur.rowcount > 0

    # ==========================
    # Analytics & Aggregates
    # ==========================

    def get_kpis(self, subject: Optional[str] = None) -> Dict[str, Any]:
        """Calculates high-level metrics for the dashboard."""
        with self.get_connection() as conn:
            base_papers_sql = "SELECT COUNT(*) as total_papers, COUNT(DISTINCT academic_year) as total_years FROM papers"
            base_q_sql = "SELECT COUNT(*) as total_questions, COUNT(DISTINCT topic) as unique_topics FROM questions"
            top_topic_sql = "SELECT topic, COUNT(*) as count FROM questions WHERE topic != 'Unclassified'"
            
            p_params = []
            q_params = []
            t_params = []

            if subject and subject != "All Subjects":
                base_papers_sql += " WHERE subject = ?"
                p_params.append(subject)
                base_q_sql += " WHERE subject = ?"
                q_params.append(subject)
                top_topic_sql += " AND subject = ?"
                t_params.append(subject)

            top_topic_sql += " GROUP BY topic ORDER BY count DESC LIMIT 1"

            papers_row = conn.execute(base_papers_sql, p_params).fetchone()
            q_row = conn.execute(base_q_sql, q_params).fetchone()
            top_t_row = conn.execute(top_topic_sql, t_params).fetchone()

            total_papers = papers_row["total_papers"] if papers_row else 0
            total_years = papers_row["total_years"] if papers_row else 0
            total_questions = q_row["total_questions"] if q_row else 0
            unique_topics = q_row["unique_topics"] if q_row else 0
            most_repeated_topic = top_t_row["topic"] if (top_t_row and top_t_row["topic"]) else "None"
            most_repeated_count = top_t_row["count"] if top_t_row else 0

            return {
                "total_papers": total_papers,
                "total_questions": total_questions,
                "unique_topics": unique_topics,
                "most_repeated_topic": most_repeated_topic,
                "most_repeated_count": most_repeated_count,
                "total_years": total_years
            }

    def get_all_subjects(self) -> List[str]:
        """Gets all distinct subjects stored in papers and questions."""
        with self.get_connection() as conn:
            cur = conn.execute("SELECT DISTINCT subject FROM papers WHERE subject IS NOT NULL AND subject != '' UNION SELECT DISTINCT subject FROM questions WHERE subject IS NOT NULL AND subject != '' ORDER BY 1")
            return [r[0] for r in cur.fetchall()]

    def get_all_years(self, subject: Optional[str] = None) -> List[str]:
        """Gets distinct academic years."""
        query = "SELECT DISTINCT academic_year FROM papers WHERE academic_year IS NOT NULL AND academic_year != ''"
        params = []
        if subject and subject != "All Subjects":
            query += " AND subject = ?"
            params.append(subject)
        query += " ORDER BY academic_year DESC"

        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return [r[0] for r in cur.fetchall()]

    def get_all_topics(self, subject: Optional[str] = None) -> List[str]:
        """Gets distinct topics."""
        query = "SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL AND topic != ''"
        params = []
        if subject and subject != "All Subjects":
            query += " AND subject = ?"
            params.append(subject)
        query += " ORDER BY topic ASC"

        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return [r[0] for r in cur.fetchall()]

    def get_all_units(self, subject: Optional[str] = None) -> List[str]:
        """Gets distinct units."""
        query = "SELECT DISTINCT unit FROM questions WHERE unit IS NOT NULL AND unit != ''"
        params = []
        if subject and subject != "All Subjects":
            query += " AND subject = ?"
            params.append(subject)
        query += " ORDER BY unit ASC"

        with self.get_connection() as conn:
            cur = conn.execute(query, params)
            return [r[0] for r in cur.fetchall()]

    def clear_all_data(self):
        """Purges all records from papers, questions, topics, and analysis_results."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM questions")
            conn.execute("DELETE FROM papers")
            conn.execute("DELETE FROM topics")
            conn.execute("DELETE FROM analysis_results")
            conn.commit()
