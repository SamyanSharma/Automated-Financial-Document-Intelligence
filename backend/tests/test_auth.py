import pytest

pytestmark = pytest.mark.asyncio


async def test_register_creates_user(client):
    resp = await client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@example.com"
    assert "id" in body
    assert "hashed_password" not in body  # never leak the hash


async def test_register_duplicate_email_rejected(client):
    payload = {"email": "dupe@example.com", "password": "password123"}
    first = await client.post("/auth/register", json=payload)
    second = await client.post("/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 400


async def test_login_success_returns_token(client):
    await client.post("/auth/register", json={"email": "b@example.com", "password": "password123"})
    resp = await client.post("/auth/login", json={"email": "b@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert len(resp.json()["access_token"]) > 20


async def test_login_wrong_password_rejected(client):
    await client.post("/auth/register", json={"email": "c@example.com", "password": "password123"})
    resp = await client.post("/auth/login", json={"email": "c@example.com", "password": "wrong"})
    assert resp.status_code == 401


async def test_login_unknown_email_rejected(client):
    resp = await client.post("/auth/login", json={"email": "nope@example.com", "password": "x"})
    assert resp.status_code == 401


async def test_register_short_password_rejected(client):
    resp = await client.post("/auth/register", json={"email": "d@example.com", "password": "short"})
    assert resp.status_code == 422  # Pydantic min_length validation
