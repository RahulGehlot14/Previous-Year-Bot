"""
Validation utilities for uploaded documents, academic years, and input data.
"""

from pathlib import Path
from typing import Tuple
from config import SUPPORTED_FORMATS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB

def validate_uploaded_file(filename: str, file_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates uploaded document:
    - Extension must be in SUPPORTED_FORMATS (.pdf, .docx, .txt).
    - File size must be greater than 0 and within MAX_FILE_SIZE_MB.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "File name cannot be empty."

    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format '{ext}'. Allowed formats: {', '.join(SUPPORTED_FORMATS)}"

    size = len(file_bytes)
    if size == 0:
        return False, "The uploaded file is empty (0 bytes)."

    if size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({size / (1024*1024):.1f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_MB} MB."

    return True, ""

def validate_academic_year(year_str: str) -> bool:
    """Validates academic year string (e.g. '2023', '2022-23', '2023-2024')."""
    if not year_str or not year_str.strip():
        return False
    clean = year_str.strip()
    return len(clean) >= 4 and any(c.isdigit() for c in clean)
