"""
Text chunking using LangChain's RecursiveCharacterTextSplitter.

How it works (per LangChain docs:
https://python.langchain.com/docs/how_to/recursive_text_splitter/):
RecursiveCharacterTextSplitter tries to split on a prioritized list of
separators (paragraph -> sentence -> word) and only falls back to a hard
character cut when a chunk still won't fit within `chunk_size`. This keeps
chunks semantically coherent (whole paragraphs/sentences where possible)
rather than cutting mid-word, which matters for embedding quality
downstream.

We chunk per-page (not the whole document concatenated) so every chunk can
be tagged with the page_number it came from, which the AI module needs for
citations. `char_start`/`char_end` are offsets within that page's text,
useful for traceability/debugging.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from services.pdf_service import PageText

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    page_number: int
    sequence: int
    char_start: int
    char_end: int


def chunk_pages(
    pages: list[PageText],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Chunk]:
    """
    Split extracted page text into overlapping chunks, preserving page
    number and a running sequence number across the whole document.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks: list[Chunk] = []
    sequence = 0

    for page in pages:
        if not page.text:
            continue

        pieces = splitter.split_text(page.text)

        # Track offsets by searching incrementally so overlapping pieces
        # still map back to a reasonable position in the page text.
        cursor = 0
        for piece in pieces:
            start = page.text.find(piece, max(0, cursor - chunk_overlap))
            if start == -1:
                start = page.text.find(piece)
            end = start + len(piece) if start != -1 else len(piece)
            cursor = end

            chunks.append(
                Chunk(
                    text=piece,
                    page_number=page.page_number,
                    sequence=sequence,
                    char_start=max(start, 0),
                    char_end=max(end, 0),
                )
            )
            sequence += 1

    logger.info("Produced %d chunks from %d pages", len(chunks), len(pages))
    return chunks
