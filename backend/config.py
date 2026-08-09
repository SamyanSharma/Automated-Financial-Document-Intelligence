"""
Application configuration using pydantic-settings.

Design decision: all secrets/config are pulled from environment variables
(or a .env file in local dev) rather than hardcoded, so the same codebase
works across dev/staging/prod without code changes. Pydantic validates
types at startup, so a missing/malformed env var fails fast instead of
causing a confusing runtime error later.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Financial Document Ingestion API"
    environment: str = "development"
    debug: bool = True

    # --- Database ---
    # Async driver required (asyncpg for Postgres). Example:
    # postgresql+asyncpg://user:password@localhost:5432/findocs
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # --- Auth / JWT ---
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"  # override via env in real deploys
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # --- File storage ---
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 25

    # --- Chunking ---
    chunk_size: int = 1000
    chunk_overlap: int = 150

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() is only constructed/parsed once per process."""
    return Settings()
