"""
Embedding generation: converts chunk text into vectors.

How it works:
- `OpenAIEmbedder` uses LangChain's `OpenAIEmbeddings` wrapper around
  OpenAI's embeddings endpoint (per LangChain docs:
  https://python.langchain.com/docs/integrations/text_embedding/openai/).
  This is the real production path — requires `OPENAI_API_KEY`.
- `LocalDeterministicEmbedder` is a dependency-free, offline fallback: a
  hashing-trick bag-of-words vectorizer (tokenize -> hash each token into
  one of `embedding_dimensions` buckets -> L2-normalize). It has none of
  a real embedding model's semantic understanding, but it IS a genuine
  vector space where documents sharing vocabulary score more similar,
  which is enough to exercise the full retrieval pipeline (store, search,
  rank) correctly without network access or an API key. Used automatically
  when `AISettings.embedding_provider == "local"` (the default), which is
  also what makes this pipeline testable in CI/sandboxes with no internet.

Both implementations share the same interface (`embed_texts`), so
swapping providers is a one-line config change everywhere else in the
codebase (vector_store.py, retriever.py never know which one is active).
"""
from __future__ import annotations

import hashlib
import logging
import math
import re
from abc import ABC, abstractmethod

from ai.config import AISettings, get_ai_settings

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Small stopword list for the local embedder only. Without this, high-
# frequency function words ("the", "a", "of") can dominate the hashed
# bag-of-words vector's dot product and outrank genuine topical overlap
# (e.g. a query about "revenue" matching a chunk on word count of "the"
# rather than the word "revenue" itself). A real embedding model doesn't
# have this failure mode; this list exists purely to keep the *offline
# fallback* usable for demonstrating correct retrieval ranking.
_STOPWORDS = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or",
    "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "this", "that", "these", "those", "as", "by", "with", "from", "into",
    "than", "then", "so", "but", "if", "not", "no", "do", "does", "did",
    "has", "have", "had", "will", "would", "can", "could", "should",
    "what", "which", "who", "whom", "how", "when", "where", "why",
}


class Embedder(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, same order."""

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


class LocalDeterministicEmbedder(Embedder):
    """Offline hashing-trick embedder. See module docstring for rationale."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _vectorize(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        # Strip apostrophes first so "company's" -> "companys" (one token)
        # instead of splitting into "company" + a noise token "s" that can
        # hash-collide with an unrelated word and skew similarity.
        cleaned = text.lower().replace("'", "")
        tokens = [
            t for t in _TOKEN_RE.findall(cleaned)
            if t not in _STOPWORDS and len(t) > 1
        ]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest, 16) % self.dimensions
            vec[bucket] += 1.0

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(t) for t in texts]


class OpenAIEmbedder(Embedder):
    """Real embeddings via LangChain's OpenAIEmbeddings. Requires an API key."""

    def __init__(self, api_key: str, model: str):
        from langchain_openai import OpenAIEmbeddings  # imported lazily: optional dep

        self._client = OpenAIEmbeddings(api_key=api_key, model=model)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self._client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._client.embed_query(text)


def get_embedder(settings: AISettings | None = None) -> Embedder:
    """Factory: returns the configured embedder, falling back to local
    if "openai" was requested but no API key is set (fail-soft, not
    fail-hard, so a misconfigured .env doesn't take the whole app down)."""
    settings = settings or get_ai_settings()

    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            logger.warning(
                "embedding_provider=openai but OPENAI_API_KEY is not set; "
                "falling back to LocalDeterministicEmbedder"
            )
            return LocalDeterministicEmbedder(settings.embedding_dimensions)
        logger.info("Using OpenAIEmbedder (model=%s)", settings.openai_embedding_model)
        return OpenAIEmbedder(settings.openai_api_key, settings.openai_embedding_model)

    logger.info("Using LocalDeterministicEmbedder (dims=%d)", settings.embedding_dimensions)
    return LocalDeterministicEmbedder(settings.embedding_dimensions)
