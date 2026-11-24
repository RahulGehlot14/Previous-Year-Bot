"""
Question Similarity & Duplication Engine for Previous Year Question Paper Analyzer.
Detects near-identical or repeating questions across different academic years
using token set overlap and Jaccard similarity.
"""

import re
from typing import List, Dict, Any, Tuple

class SimilarityEngine:
    """Finds repeated question templates and recurring wording across examination years."""

    @staticmethod
    def _tokenize(text: str) -> set:
        """Tokenizes text into cleaned lower-case keyword tokens."""
        words = re.findall(r"\b[a-z]{3,}\b", text.lower())
        stopwords = {
            "what", "when", "where", "which", "explain", "describe", "discuss",
            "define", "between", "following", "with", "from", "that", "this",
            "have", "some", "your", "marks", "state", "differentiate"
        }
        return {w for w in words if w not in stopwords}

    @classmethod
    def calculate_similarity(cls, text1: str, text2: str) -> float:
        """Computes Jaccard similarity coefficient between two question texts."""
        set1 = cls._tokenize(text1)
        set2 = cls._tokenize(text2)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return round(intersection / union, 2)

    @classmethod
    def find_cross_year_duplicates(cls, questions: List[Dict[str, Any]],
                                   threshold: float = 0.40) -> List[Dict[str, Any]]:
        """
        Finds pairs of questions from DIFFERENT academic years that share high similarity.
        Highlights how examiners repeat question phrasing.
        """
        if len(questions) < 2:
            return []

        similar_pairs = []
        n = len(questions)

        for i in range(n):
            q1 = questions[i]
            for j in range(i + 1, n):
                q2 = questions[j]

                # Check if they are from different academic years
                if q1.get("academic_year") != q2.get("academic_year"):
                    sim = cls.calculate_similarity(q1.get("question_text", ""), q2.get("question_text", ""))
                    if sim >= threshold:
                        similar_pairs.append({
                            "similarity_pct": int(sim * 100),
                            "topic": q1.get("topic", "General"),
                            "q1_year": q1.get("academic_year"),
                            "q1_number": q1.get("question_number"),
                            "q1_text": q1.get("question_text"),
                            "q2_year": q2.get("academic_year"),
                            "q2_number": q2.get("question_number"),
                            "q2_text": q2.get("question_text"),
                        })

        # Sort pairs by similarity descending
        similar_pairs.sort(key=lambda x: x["similarity_pct"], reverse=True)
        return similar_pairs
