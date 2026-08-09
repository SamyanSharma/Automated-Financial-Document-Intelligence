"""
Async DB engine + session management (SQLAlchemy 2.0 style).

Design decision: we use an async engine/session everywhere (not the legacy
sync Session) because this API does I/O-bound work (DB + PDF parsing can
be offloaded) and we want the event loop free to serve concurrent uploads.

get_db() is a FastAPI dependency that yields one session per request and
guarantees it's closed afterward, even on error.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keep objects usable after commit (e.g. for response serialization)
    autoflush=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""
    pass


async def get_db():
    """FastAPI dependency: yields an AsyncSession, always closes it."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("DB session error - rolling back")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Create tables from metadata. Used for local/dev bootstrap and tests.
    In staging/prod, Alembic migrations are the source of truth instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured (init_db)")
