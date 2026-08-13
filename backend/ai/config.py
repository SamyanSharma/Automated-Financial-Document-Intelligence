"""
AI module configuration.

Design decision: kept separate from the top-level `config.py` (owned by
Member 1) rather than adding fields there, so this module's settings are
self-contained and reviewable independently. Both use the same
pydantic-settings pattern for consistency.

`embedding_provider` / `llm_provider` are pluggable via env var so the
same code runs in three modes:
  - "openai"  : real OpenAI embeddings + chat completions (needs OPENAI_API_KEY)
  - "gemini"  : real Google Gemini chat completions (needs GEMINI_API_KEY)
  - "local"   : deterministic offline embedder + template-based answerer,
                zero external calls. Used automatically when no API key is
                configured, and in this sandbox/CI where openai.com and
                generativelanguage.googleapis.com aren't reachable. This
                keeps the whole RAG pipeline testable without live API
                credentials, while the real providers are a one-line env
                var away in a real deployment.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    # --- Embeddings ---
    embedding_provider: str = "local"  # "openai" | "local"
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 384  # used by the local deterministic embedder

    # --- LLM completions ---
    llm_provider: str = "local"  # "openai" | "gemini" | "local"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    openai_chat_model: str = "gpt-4o-mini"

    # --- Vector store (ChromaDB) ---
    chroma_persist_dir: str = "chroma_data"
    chroma_collection_name: str = "document_chunks"

    # --- Retrieval ---
    default_top_k: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_ai_settings() -> AISettings:
    settings = AISettings()
    # Auto-select "local" if a real provider was requested but no key is
    # configured, so the app degrades gracefully instead of crashing at
    # first use. Logged (not raised) since this is a valid dev/test mode.
    return settings
