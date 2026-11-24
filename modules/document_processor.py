"""
Document Processor Module for Previous Year Question Paper Analyzer.
Extracts and cleans text from PDF, DOCX, and TXT files.
Includes scanned PDF detection and graceful OCR support via pytesseract.
"""

import io
import re
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

import fitz  # PyMuPDF
from docx import Document
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from utils.helpers import clean_text

class DocumentProcessor:
    """Handles text extraction and preprocessing from various document formats."""

    @staticmethod
    def extract_text(file_source: Any, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts clean text from a file path or file-like bytes object.
        Returns (cleaned_text, metadata).
        """
        ext = Path(filename).suffix.lower()
        metadata: Dict[str, Any] = {
            "filename": filename,
            "format": ext,
            "is_scanned": False,
            "ocr_used": False,
            "ocr_warning": None,
            "page_count": 0,
            "char_count": 0
        }

        # Convert to bytes if not already
        if isinstance(file_source, (str, Path)):
            with open(file_source, "rb") as f:
                file_bytes = f.read()
        elif hasattr(file_source, "read"):
            file_bytes = file_source.read()
            if hasattr(file_source, "seek"):
                file_source.seek(0)
        elif isinstance(file_source, bytes):
            file_bytes = file_source
        else:
            raise ValueError(f"Unsupported file source type: {type(file_source)}")

        if not file_bytes:
            raise ValueError(f"File '{filename}' is empty (0 bytes).")

        raw_text = ""
        if ext == ".pdf":
            raw_text, metadata = DocumentProcessor._extract_pdf(file_bytes, metadata)
        elif ext == ".docx":
            raw_text, metadata = DocumentProcessor._extract_docx(file_bytes, metadata)
        elif ext == ".txt":
            raw_text, metadata = DocumentProcessor._extract_txt(file_bytes, metadata)
        else:
            raise ValueError(f"Unsupported file extension '{ext}'. Expected .pdf, .docx, or .txt.")

        cleaned = clean_text(raw_text)
        metadata["char_count"] = len(cleaned)

        if not cleaned.strip():
            if metadata.get("is_scanned") and not metadata.get("ocr_used"):
                raise ValueError(
                    f"Document '{filename}' appears to be a scanned image-only PDF. "
                    "Text extraction requires Tesseract-OCR to be installed on your system."
                )
            raise ValueError(f"No extractable text found in '{filename}'. The document may be empty or unreadable.")

        return cleaned, metadata

    @staticmethod
    def _extract_pdf(file_bytes: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Extracts text from PDF with automatic scanned document detection and OCR fallback."""
        text_parts = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Failed to open PDF document. File may be corrupted or password protected. Details: {str(e)}")

        page_count = len(doc)
        metadata["page_count"] = page_count

        total_extracted_chars = 0
        pages_text = []

        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            text = page.get_text("text") or ""
            pages_text.append(text)
            total_extracted_chars += len(text.strip())

        avg_chars_per_page = total_extracted_chars / max(1, page_count)

        # Detect scanned PDF (average less than 40 chars per page indicates image-only/scanned PDF)
        if avg_chars_per_page < 40 and page_count > 0:
            metadata["is_scanned"] = True
            if PYTESSERACT_AVAILABLE:
                try:
                    ocr_text_parts = []
                    for page_idx in range(page_count):
                        page = doc.load_page(page_idx)
                        # Render page to high-res pixmap for OCR
                        pix = page.get_pixmap(dpi=200)
                        img_bytes = pix.tobytes("png")
                        image = Image.open(io.BytesIO(img_bytes))
                        ocr_result = pytesseract.image_to_string(image)
                        ocr_text_parts.append(ocr_result)

                    combined_ocr = "\n".join(ocr_text_parts)
                    if len(combined_ocr.strip()) > total_extracted_chars:
                        metadata["ocr_used"] = True
                        return combined_ocr, metadata
                except Exception as ocr_err:
                    metadata["ocr_warning"] = (
                        f"OCR processing failed: {str(ocr_err)}. "
                        "Ensure the Tesseract binary is installed and in your system PATH."
                    )
            else:
                metadata["ocr_warning"] = "Scanned PDF detected, but 'pytesseract' is not installed."

        doc.close()
        return "\n".join(pages_text), metadata

    @staticmethod
    def _extract_docx(file_bytes: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Extracts text from DOCX paragraphs and tables."""
        try:
            doc = Document(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Failed to read DOCX file. Document may be corrupted. Details: {str(e)}")

        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        # Extract table cells
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    table_texts.append(" | ".join(row_cells))

        combined = "\n\n".join(paragraphs + table_texts)
        metadata["page_count"] = max(1, len(paragraphs) // 15)  # approximate page count
        return combined, metadata

    @staticmethod
    def _extract_txt(file_bytes: bytes, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Extracts text from TXT with multiple encoding attempts."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]
        for enc in encodings:
            try:
                decoded = file_bytes.decode(enc)
                metadata["page_count"] = max(1, len(decoded) // 2000)
                return decoded, metadata
            except UnicodeDecodeError:
                continue

        # Fallback with error replacement
        decoded = file_bytes.decode("utf-8", errors="replace")
        metadata["page_count"] = max(1, len(decoded) // 2000)
        return decoded, metadata
