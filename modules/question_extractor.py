"""
Question Extractor Module for Previous Year Question Paper Analyzer.
Identifies question patterns, separates individual questions and subquestions,
detects marks allocation, and formats into structured question objects.
"""

import re
from typing import List, Dict, Any, Optional

class QuestionExtractor:
    """Extracts individual questions and marks from raw exam paper text."""

    # Patterns for question headers:
    # 1. "Q1", "Q.1", "Question 1", "QUESTION 1:", "Q 1"
    # 2. "1.", "2.", "3.", "1)", "2)", "3)"
    # 3. Roman numerals: "I.", "II.", "III."
    QUESTION_START_PATTERN = re.compile(
        r"^(?:\s*)(?:"
        r"(?:Q(?:uestion)?[\s\.\:\-]*(?:\d+|[IVXLCDM]+)[\.\:\-]*)"  # Q1, Q1., Question 2:, Q.1
        r"|(?:\d{1,2}[\.\)])"                                      # 1., 2)
        r"|(?:\(\d{1,2}\))"                                        # (1), (2)
        r"|(?:[IVXLCDM]{1,4}[\.\)])"                               # I., II)
        r")\s+",
        re.IGNORECASE
    )

    # Subquestion pattern: a), b), c), (a), (b), (i), (ii), etc.
    SUBQUESTION_PATTERN = re.compile(
        r"^(?:\s*)(?:"
        r"(?:\(?[a-hA-H]\))"        # a), (a), A), (A)
        r"|(?:\(?[iIvVxX]{1,4}\))"  # (i), (ii), i), ii)
        r"|(?:[a-hA-H]\.)"          # a., b.
        r")\s+"
    )

    # Marks regex: [5 Marks], (10), [CO1, 7M], [10 Marks], 5M, 10 marks
    MARKS_PATTERN = re.compile(
        r"(?:\[|\()?\s*(?:(?:CO\d+|BL\d+|L\d+)[,\s]*)?(\d{1,2})\s*(?:marks?|mark|m)?\s*(?:\]|\))|"
        r"\[\s*(\d{1,2})\s*\]|"
        r"\(\s*(\d{1,2})\s*\)$",
        re.IGNORECASE
    )

    @classmethod
    def extract_questions(cls, text: str, filename: str = "",
                          subject: str = "", academic_year: str = "") -> List[Dict[str, Any]]:
        """
        Parses full exam paper text and extracts discrete questions.
        Returns a list of structured question dictionaries.
        """
        if not text or not text.strip():
            return []

        # Split into candidate blocks based on question delimiters
        questions: List[Dict[str, Any]] = []
        lines = text.split("\n")
        
        current_base_num = ""
        current_q_num = ""
        current_q_lines: List[str] = []
        q_counter = 1
        has_started = False

        def finalize_question(num_str: str, lines_list: List[str]):
            nonlocal q_counter
            q_text = "\n".join(lines_list).strip()
            if not q_text or len(q_text) < 10:
                return

            marks = cls._extract_marks(q_text)
            # Remove marks annotations from question text for cleaner presentation
            cleaned_text = cls._clean_marks_from_text(q_text)

            assigned_num = num_str if num_str else f"Q{q_counter}"
            q_id = f"{academic_year}_{assigned_num}".replace(" ", "_").replace(".", "_").replace("(", "").replace(")", "")
            if not q_id or q_id.startswith("_"):
                q_id = f"Q{q_counter:03d}"

            questions.append({
                "question_id": f"Q{q_counter:03d}",
                "question_number": assigned_num,
                "question_text": cleaned_text,
                "marks": marks,
                "subject": subject,
                "academic_year": academic_year,
                "source_document": filename,
                "unit": "General",
                "topic": "Unclassified",
                "subtopic": "",
                "keywords": [],
                "question_type": "Theory",
                "difficulty": "Medium",
                "bloom_level": "Understand",
                "classification_source": "rule_based"
            })
            q_counter += 1

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if current_q_lines:
                    current_q_lines.append("")
                continue

            # Check if line starts with a primary question marker
            match = cls.QUESTION_START_PATTERN.match(line)
            if match:
                has_started = True
                # Save prior question if accumulated
                if current_q_lines:
                    finalize_question(current_q_num, current_q_lines)
                    current_q_lines = []

                matched_prefix = match.group(0).strip()
                clean_num = re.sub(r"[^\w\.]", "", matched_prefix)
                current_base_num = clean_num if clean_num else f"Q{q_counter}"
                current_q_num = current_base_num

                content_after = line[match.end():].strip()
                if content_after:
                    current_q_lines.append(content_after)
            elif not has_started:
                # Still in header boilerplate before first question
                continue
            else:
                # Check for subquestion inside an existing question
                sub_match = cls.SUBQUESTION_PATTERN.match(line)
                if sub_match and current_q_lines:
                    sub_prefix = sub_match.group(0).strip()
                    sub_clean = sub_prefix.strip("(). ")
                    sub_content = line[sub_match.end():].strip()

                    # Finalize parent question if substantive
                    if len(" ".join(current_q_lines).strip()) >= 25:
                        finalize_question(current_q_num, current_q_lines)
                    current_q_num = f"{current_base_num}({sub_clean})"
                    current_q_lines = [sub_content] if sub_content else []
                else:
                    current_q_lines.append(line_stripped)

        # Finalize last question block
        if current_q_lines:
            finalize_question(current_q_num, current_q_lines)

        # Fallback: if structured numbering was not detected (e.g. unnumbered questions list)
        if not questions and len(text.strip()) > 30:
            questions = cls._fallback_paragraph_extractor(text, filename, subject, academic_year)

        return questions

    @classmethod
    def _extract_marks(cls, text: str) -> Optional[float]:
        """Detects marks in question text."""
        # Check end of text first
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return None

        # Search in the full text from end to beginning
        matches = list(cls.MARKS_PATTERN.finditer(text))
        if matches:
            last_match = matches[-1]
            for g in last_match.groups():
                if g and g.isdigit():
                    val = float(g)
                    if 1 <= val <= 100:
                        return val
        return None

    @classmethod
    def _clean_marks_from_text(cls, text: str) -> str:
        """Removes explicit marks markers (e.g., '[10 Marks]') from end of question for clean storage."""
        cleaned = cls.MARKS_PATTERN.sub("", text)
        return cleaned.strip()

    @classmethod
    def _fallback_paragraph_extractor(cls, text: str, filename: str,
                                      subject: str, academic_year: str) -> List[Dict[str, Any]]:
        """Fallback splitter when standard numbering is absent."""
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 15]
        results = []
        for idx, para in enumerate(paragraphs, 1):
            results.append({
                "question_id": f"Q{idx:03d}",
                "question_number": f"Q{idx}",
                "question_text": para,
                "marks": cls._extract_marks(para),
                "subject": subject,
                "academic_year": academic_year,
                "source_document": filename,
                "unit": "General",
                "topic": "Unclassified",
                "subtopic": "",
                "keywords": [],
                "question_type": "Theory",
                "difficulty": "Medium",
                "bloom_level": "Understand",
                "classification_source": "rule_based"
            })
        return results
