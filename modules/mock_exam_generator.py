"""
Mock Exam Paper Generator Module for Previous Year Question Paper Analyzer.
Assembles realistic, syllabus-balanced mock examination papers
from historical questions matching standard university formats.
"""

from typing import List, Dict, Any, Optional
import random

class MockExamGenerator:
    """Constructs balanced practice examination papers from the question bank."""

    @classmethod
    def generate_mock_paper(cls, questions: List[Dict[str, Any]],
                            subject: str,
                            total_marks: int = 100,
                            duration_hours: int = 3) -> Dict[str, Any]:
        """
        Creates an authentic practice exam paper:
        - Groups questions by syllabus unit.
        - Selects a balanced mix of short and long questions.
        - Calculates total marks and instructions.
        """
        if not questions:
            return {"error": "No questions available to generate mock exam."}

        # Segregate by units
        unit_map: Dict[str, List[Dict[str, Any]]] = {}
        for q in questions:
            u = q.get("unit", "Unit 1")
            if u not in unit_map:
                unit_map[u] = []
            unit_map[u].append(q)

        selected_questions: List[Dict[str, Any]] = []
        accumulated_marks = 0
        sorted_units = sorted(unit_map.keys())

        # Attempt to pick 1-2 questions from each unit
        q_num = 1
        for u in sorted_units:
            pool = list(unit_map[u])
            random.shuffle(pool)

            # Pick top 2 questions from this unit
            for candidate in pool[:2]:
                marks_val = candidate.get("marks") or 10.0
                if accumulated_marks + marks_val <= total_marks or len(selected_questions) < 5:
                    item = dict(candidate)
                    item["mock_question_number"] = f"Q{q_num}"
                    item["assigned_marks"] = marks_val
                    selected_questions.append(item)
                    accumulated_marks += marks_val
                    q_num += 1

                if accumulated_marks >= total_marks:
                    break
            if accumulated_marks >= total_marks:
                break

        # If total marks is still below target, pick from remaining questions
        all_remaining = [q for q in questions if q["id"] not in [sq["id"] for sq in selected_questions]]
        random.shuffle(all_remaining)

        for candidate in all_remaining:
            if accumulated_marks >= total_marks:
                break
            marks_val = candidate.get("marks") or 10.0
            item = dict(candidate)
            item["mock_question_number"] = f"Q{q_num}"
            item["assigned_marks"] = marks_val
            selected_questions.append(item)
            accumulated_marks += marks_val
            q_num += 1

        return {
            "title": f"MOCK EXAMINATION - {subject.upper()}",
            "subject": subject,
            "duration": f"{duration_hours} Hours",
            "total_marks": int(accumulated_marks),
            "instructions": [
                "1. All questions carry indicated marks.",
                "2. Answer all questions concisely with appropriate diagrams where applicable.",
                "3. Assume suitable data if necessary and state the assumptions clearly."
            ],
            "questions": selected_questions
        }
