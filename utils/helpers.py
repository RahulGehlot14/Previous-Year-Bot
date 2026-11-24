"""
Utility Helpers for hashing, formatting, text cleaning, and JSON operations.
"""

import hashlib
import json
import re
from typing import Any, Optional

def compute_file_hash(file_bytes: bytes) -> str:
    """Computes SHA-256 hash of file contents to detect duplicates."""
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

def format_bytes(size_bytes: int) -> str:
    """Formats file size into human-readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def clean_text(raw_text: str) -> str:
    """
    Cleans raw document text:
    - Normalizes line breaks and whitespace.
    - Strips noisy headers/footers (page numbers, exam timestamps, student roll lines).
    - Preserves mathematical symbols, relational algebra, and question markers.
    """
    if not raw_text:
        return ""

    # Replace carriage returns
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove standard header/footer boilerplate common in exam papers
    boilerplates = [
        r"(?i)Page\s+\d+\s+of\s+\d+",
        r"(?i)Roll\s+No\s*[:\.]?\s*[_\.\s\-]+",
        r"(?i)Total\s+No\.\s+of\s+Questions\s*[:\.]?\s*\d+",
        r"(?i)Total\s+No\.\s+of\s+Printed\s+Pages\s*[:\.]?\s*\d+",
        r"(?i)Time\s*Allowed\s*[:\.]?\s*\d+\s*(?:Hours?|Hrs?)",
        r"(?i)Maximum\s*Marks\s*[:\.]?\s*\d+",
        r"(?i)Max\s*Marks\s*[:\.]?\s*\d+",
        r"(?i)All\s+questions\s+are\s+compulsory\.?",
        r"(?i)Attempt\s+any\s+(?:five|all|\d+)\s+questions\.?"
    ]
    for pattern in boilerplates:
        text = re.sub(pattern, " ", text)

    # Normalize excessive spaces on lines while preserving newlines
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Collapse more than two consecutive empty lines
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parses JSON strings, including extracting JSON from markdown code fences."""
    if not json_str:
        return default
    
    clean_str = json_str.strip()
    # Strip markdown block if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_str)
    if match:
        clean_str = match.group(1).strip()
        
    try:
        return json.loads(clean_str)
    except Exception:
        # Try finding outermost list or dict
        try:
            start_bracket = clean_str.find("[")
            end_bracket = clean_str.rfind("]")
            if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
                return json.loads(clean_str[start_bracket:end_bracket+1])
            start_brace = clean_str.find("{")
            end_brace = clean_str.rfind("}")
            if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                return json.loads(clean_str[start_brace:end_brace+1])
        except Exception:
            pass
    return default
