"""
Semantic search: embed a user's question, query the vector store, return
the top-k relevant chunks with their source metadata.

This is intentionally a thin orchestration layer — embedding_service.py
and vector_store.py each already do one job well; retriever.py's only
responsibility is wiring them together the way the RAG pipeline needs
(embed the query with the *same* embedder used to index the chunks,
then hand the query vector to the vector store).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from ai.config import AISettings, get_ai_settings
from ai.embedding_service import Embedder, get_embedder
from ai.vector_store import VectorStore, get_vector_store

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    document_id: str
    page_number: int
    sequence: int
    distance: float


def retrieve(
    query: str,
    document_id: str | None = None,
    k: int | None = None,
    embedder: Embedder | None = None,
    store: VectorStore | None = None,
    settings: AISettings | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieve the top-k chunks most relevant to `query`.

    If `document_id` is given, search is scoped to that document only
    (the typical case: answering a question about one uploaded report).
    Omit it to search across all embedded documents.
    """
    settings = settings or get_ai_settings()
    embedder = embedder or get_embedder(settings)
    store = store or get_vector_store()
    k = k or settings.default_top_k

    query_vector = embedder.embed_query(query)
    hits = store.similarity_search(query_vector, k=k, document_id=document_id)

    results = [
        RetrievedChunk(
            chunk_id=h["id"],
            text=h["text"],
            document_id=h["metadata"]["document_id"],
            page_number=h["metadata"]["page_number"],
            sequence=h["metadata"]["sequence"],
            distance=h["distance"],
        )
        for h in hits
    ]
    logger.info("retrieve(query=%r, document_id=%s) -> %d chunks", query[:60], document_id, len(results))
    return results
