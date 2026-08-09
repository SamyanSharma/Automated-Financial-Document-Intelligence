"""
Test fixtures: an isolated in-memory SQLite DB per test run, and an httpx
AsyncClient wired to the FastAPI app via ASGITransport (no real network
socket needed). Using in-memory SQLite keeps tests fast and side-effect
free (nothing touches dev.db or a real Postgres instance).
"""
import os
import shutil

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["UPLOAD_DIR"] = "test_uploads"

import database  # noqa: E402
import main  # noqa: E402
import models  # noqa: E402,F401


@pytest_asyncio.fixture
async def client():
    # Fresh engine/session per test so tables are recreated cleanly.
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    database.engine = test_engine
    database.AsyncSessionLocal = async_sessionmaker(
        bind=test_engine, class_=database.AsyncSession, expire_on_commit=False
    )
    # documents.py imported AsyncSessionLocal by reference at import time;
    # patch it there too so the background task uses the same test engine.
    import routers.documents as documents_module
    documents_module.AsyncSessionLocal = database.AsyncSessionLocal

    async with test_engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)

    os.makedirs("test_uploads", exist_ok=True)

    transport = ASGITransport(app=main.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await test_engine.dispose()
    shutil.rmtree("test_uploads", ignore_errors=True)


@pytest_asyncio.fixture
async def auth_headers(client):
    await client.post(
        "/auth/register", json={"email": "pytest@example.com", "password": "testpassword123"}
    )
    resp = await client.post(
        "/auth/login", json={"email": "pytest@example.com", "password": "testpassword123"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
