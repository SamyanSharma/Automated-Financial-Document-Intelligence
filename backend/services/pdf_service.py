"""
PDF text extraction using PyMuPDF (fitz).

How it works (per PyMuPDF docs: https://pymupdf.readthedocs.io/):
- `fitz.open(path)` opens the PDF and gives us a Document object we can
  iterate page by page.
- `page.get_text("text")` extracts plain reading-order text for that page.
  We use the "text" mode (not "blocks"/"dict") because we just need clean
  text for chunking/embeddings, not layout geometry.

Header/footer stripping heuristic:
Financial reports commonly repeat a header (company name / report title)
and a footer (page number, confidentiality notice) on every page. We
detect this by taking the first and last non-empty line of every page; if
the *same* line (after normalizing whitespace/digits) appears on more than
60% of pages, we treat it as a repeated header/footer and strip it from
every page. This is a cheap heuristic, not perfect OCR-level layout
analysis, but works well for typical repeated boilerplate.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be opened or text cannot be extracted."""


@dataclass
class PageText:
    page_number: int  # 1-indexed, human-friendly for citations
    text: str


def _normalize_line(line: str) -> str:
    """Collapse whitespace and digits so 'Page 3 of 40' and 'Page 4 of 40'
    are recognized as the same repeated pattern."""
    line = line.strip().lower()
    line = re.sub(r"\d+", "#", line)
    line = re.sub(r"\s+", " ", line)
    return line


def _find_repeated_lines(pages_raw: list[list[str]]) -> set[str]:
    """Given each page's list of non-empty lines, find normalized lines
    that repeat across most pages (likely headers/footers)."""
    if len(pages_raw) < 3:
        return set()  # too few pages to safely detect a pattern

    from collections import Counter

    counter: Counter[str] = Counter()
    for lines in pages_raw:
        candidates = set()
        if lines:
            candidates.add(_normalize_line(lines[0]))
            candidates.add(_normalize_line(lines[-1]))
        for c in candidates:
            if c:
                counter[c] += 1

    threshold = max(2, int(len(pages_raw) * 0.6))
    return {line for line, count in counter.items() if count >= threshold}


def extract_text_by_page(file_path: str, strip_repeated_boilerplate: bool = True) -> list[PageText]:
    """
    Open a PDF and return extracted text for every page.

    Raises PDFExtractionError on any failure (corrupt file, encrypted
    without password, zero pages, etc.) so callers can mark the document
    as failed with a clear message.
    """
    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        logger.exception("Failed to open PDF at %s", file_path)
        raise PDFExtractionError(f"Could not open PDF: {exc}") from exc

    try:
        if doc.is_encrypted:
            raise PDFExtractionError("PDF is encrypted/password-protected")

        if doc.page_count == 0:
            raise PDFExtractionError("PDF has no pages")

        raw_pages: list[list[str]] = []
        for page in doc:
            text = page.get_text("text")
            lines = [ln for ln in text.splitlines() if ln.strip()]
            raw_pages.append(lines)

        repeated = _find_repeated_lines(raw_pages) if strip_repeated_boilerplate else set()

        results: list[PageText] = []
        for i, lines in enumerate(raw_pages):
            if repeated:
                lines = [ln for ln in lines if _normalize_line(ln) not in repeated]
            page_text = "\n".join(lines).strip()
            results.append(PageText(page_number=i + 1, text=page_text))

        non_empty_pages = sum(1 for p in results if p.text)
        if non_empty_pages == 0:
            raise PDFExtractionError(
                "No extractable text found (PDF may be a scanned image without OCR)"
            )

        logger.info(
            "Extracted text from %d/%d pages of %s", non_empty_pages, len(results), file_path
        )
        return results
    finally:
        doc.close()
