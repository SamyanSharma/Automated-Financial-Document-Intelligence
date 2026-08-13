"""
Vector store wrapper around ChromaDB.

How it works (per ChromaDB docs: https://docs.trychroma.com/):
`chromadb.PersistentClient(path=...)` writes to disk (SQLite + Parquet
under the hood) so embeddings survive an app restart — this satisfies the
spec's "ensure persistence" requirement directly; there is no separate
step needed, PersistentClient IS the persistence.

We always pass `embeddings=` explicitly on `add()`/`query()` rather than
registering a Chroma `embedding_function`. This is deliberate: Chroma's
default embedding function downloads an ONNX model from HuggingFace on
first use, which (a) requires network access this pipeline shouldn't
depend on for a vector DB operation, and (b) would silently use a
different model than whatever `embedding_service.py` is configured to
use. Passing embeddings explicitly keeps embedding generation and vector
storage as two clearly separate, independently swappable concerns.

One collection is used for all documents; `document_id` is stored as
metadata on every chunk so retrieval can filter to a single document via
Chroma's `where` clause instead of needing one collection per document.
"""
from __future__ import annotations

import logging

import chromadb

from ai.config import AISettings, get_ai_settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, settings: AISettings | None = None):
        self.settings = settings or get_ai_settings()
        self._client = chromadb.PersistentClient(path=self.settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore ready: collection=%s persist_dir=%s (count=%d)",
            self.settings.chroma_collection_name,
            self.settings.chroma_persist_dir,
            self._collection.count(),
        )

    def add_chunks(
        self,
        chunk_ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        document_id: str,
        page_numbers: list[int],
        sequences: list[int],
    ) -> int:
        """Upsert chunks for a document. Upsert (not add) so re-embedding
        a document is idempotent instead of erroring on duplicate IDs."""
        if not chunk_ids:
            return 0

        metadatas = [
            {"document_id": document_id, "page_number": page, "sequence": seq}
            for page, seq in zip(page_numbers, sequences)
        ]

        self._collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info("Upserted %d chunks for document %s into vector store", len(chunk_ids), document_id)
        return len(chunk_ids)

    def similarity_search(
        self,
        query_embedding: list[float],
        k: int = 3,
        document_id: str | None = None,
    ) -> list[dict]:
        """
        Query the collection for the top-k most similar chunks.
        Returns a list of {text, metadata, distance} dicts, closest first.
        """
        where = {"document_id": document_id} if document_id else None

        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
        )

        hits: list[dict] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]

        for chunk_id, text, meta, dist in zip(ids, docs, metas, dists):
            hits.append({"id": chunk_id, "text": text, "metadata": meta, "distance": dist})

        logger.info("similarity_search: k=%d document_id=%s -> %d hits", k, document_id, len(hits))
        return hits

    def delete_document(self, document_id: str) -> None:
        """Remove all chunks for a document (e.g. if it's re-processed)."""
        self._collection.delete(where={"document_id": document_id})
        logger.info("Deleted vectors for document %s", document_id)


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Module-level singleton so we don't reopen the persistent Chroma
    client (and its on-disk index) on every request."""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
