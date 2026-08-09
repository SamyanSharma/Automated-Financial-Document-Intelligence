"""
Extra extraction logic that doesn't belong in pdf_service (raw extraction)
or chunk_service (splitting).

Currently: lightweight document-level metadata guesses that are cheap to
compute here (no LLM call) and useful as a dashboard preview / progress
log line. This is intentionally simple heuristics only - Member 2's AI
layer is responsible for anything requiring real understanding.
"""
from __future__ import annotations

import logging

from services.pdf_service import PageText

logger = logging.getLogger(__name__)


def guess_document_title(pages: list[PageText]) -> str | None:
    """
    Best-effort guess at a document title: the first non-trivial line of
    the first page with extractable text (e.g. often the report title /
    company name on a financial report's cover page).
    """
    for page in pages:
        for line in page.text.splitlines():
            line = line.strip()
            if len(line) >= 4:
                logger.debug("Guessed document title: %s", line)
                return line
    return None


def total_extracted_characters(pages: list[PageText]) -> int:
    """Simple stat used for progress logging / sanity checks."""
    return sum(len(p.text) for p in pages)
