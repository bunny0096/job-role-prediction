"""Helpers for extracting plain text from uploaded resume files."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


class ResumeParsingError(Exception):
    """Raised when resume text extraction fails."""


def extract_text(file_name: str, file_bytes: bytes) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".txt":
        return _extract_text_from_txt(file_bytes)
    if suffix == ".pdf":
        return _extract_text_from_pdf(file_bytes)
    if suffix == ".docx":
        return _extract_text_from_docx(file_bytes)
    raise ResumeParsingError("Unsupported file type. Use PDF, DOCX, or TXT.")


def _extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # noqa: BLE001
        raise ResumeParsingError("Unable to read PDF file.") from exc
    return "\n".join(pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        document = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in document.paragraphs]
    except Exception as exc:  # noqa: BLE001
        raise ResumeParsingError("Unable to read DOCX file.") from exc
    return "\n".join(paragraphs)
