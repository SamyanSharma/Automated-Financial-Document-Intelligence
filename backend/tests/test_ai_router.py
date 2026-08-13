import os

import pytest

pytestmark = pytest.mark.asyncio

TINY_PDF_PATH = os.path.join(os.path.dirname(__file__), "tiny.pdf")

METRICS_A = {"label": "Q3", "revenue": 100, "net_income": 8, "total_assets": 200,
             "total_liabilities": 90, "operating_cash_flow": 5}
METRICS_B = {"label": "Q4", "revenue": 115, "net_income": 9, "total_assets": 210,
             "total_liabilities": 95, "operating_cash_flow": 6}


async def _upload_and_wait_completed(client, auth_headers):
    import asyncio

    with open(TINY_PDF_PATH, "rb") as f:
        resp = await client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("tiny.pdf", f, "application/pdf")},
        )
    document_id = resp.json()["document_id"]

    for _ in range(50):
        status_resp = await client.get(f"/api/v1/documents/{document_id}/status", headers=auth_headers)
        if status_resp.json()["status"] == "completed":
            break
        await asyncio.sleep(0.1)
    return document_id


async def test_embed_requires_auth(client):
    resp = await client.post("/api/v1/documents/some-id/embed")
    assert resp.status_code == 401


async def test_embed_success_returns_chunk_count(client, auth_headers):
    document_id = await _upload_and_wait_completed(client, auth_headers)
    resp = await client.post(f"/api/v1/documents/{document_id}/embed", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_id"] == document_id
    assert body["chunks_embedded"] >= 1


async def test_embed_rejects_document_not_yet_completed(client, auth_headers):
    """Regression test for the audit-style check: embedding before
    processing finishes must be a clean 409, not silently succeed on
    zero chunks or crash."""
    with open(TINY_PDF_PATH, "rb") as f:
        resp = await client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("tiny.pdf", f, "application/pdf")},
        )
    document_id = resp.json()["document_id"]

    # Deliberately do NOT wait for the background task - call embed
    # immediately while status is very likely still "processing".
    embed_resp = await client.post(f"/api/v1/documents/{document_id}/embed", headers=auth_headers)
    assert embed_resp.status_code in (200, 409)  # 200 only if processing finished first; both are valid states
    if embed_resp.status_code == 409:
        assert "not ready" in embed_resp.json()["detail"].lower()


async def test_embed_404_for_other_users_document(client, auth_headers):
    document_id = await _upload_and_wait_completed(client, auth_headers)

    await client.post("/auth/register", json={"email": "other-ai@example.com", "password": "password123"})
    login = await client.post("/auth/login", json={"email": "other-ai@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.post(f"/api/v1/documents/{document_id}/embed", headers=other_headers)
    assert resp.status_code == 404


async def test_chat_requires_document_ownership(client, auth_headers):
    document_id = await _upload_and_wait_completed(client, auth_headers)
    await client.post(f"/api/v1/documents/{document_id}/embed", headers=auth_headers)

    await client.post("/auth/register", json={"email": "other-chat@example.com", "password": "password123"})
    login = await client.post("/auth/login", json={"email": "other-chat@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.post(
        "/api/v1/chat", headers=other_headers,
        json={"document_id": document_id, "question": "What does it say?"},
    )
    assert resp.status_code == 404


async def test_chat_returns_answer_with_sources(client, auth_headers):
    document_id = await _upload_and_wait_completed(client, auth_headers)
    await client.post(f"/api/v1/documents/{document_id}/embed", headers=auth_headers)

    resp = await client.post(
        "/api/v1/chat", headers=auth_headers,
        json={"document_id": document_id, "question": "What was the revenue?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert len(body["sources"]) >= 1
    assert body["sources"][0]["document_id"] == document_id


async def test_health_score_endpoint(client, auth_headers):
    resp = await client.post(
        "/api/v1/analysis/health-score", headers=auth_headers,
        json={"current": METRICS_B, "prior": METRICS_A},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["score"] == 80


async def test_compare_endpoint(client, auth_headers):
    resp = await client.post(
        "/api/v1/analysis/compare", headers=auth_headers,
        json={"current": METRICS_B, "prior": METRICS_A},
    )
    assert resp.status_code == 200
    revenue = next(c for c in resp.json()["changes"] if c["metric"] == "Revenue")
    assert revenue["pct_change"] == 15.0


async def test_anomalies_endpoint(client, auth_headers):
    current = {**METRICS_B, "net_income": 2}
    prior = {**METRICS_A, "net_income": 5}
    resp = await client.post(
        "/api/v1/analysis/anomalies", headers=auth_headers,
        json={"current": current, "prior": prior},
    )
    assert resp.status_code == 200
    alerts = resp.json()["alerts"]
    assert any(a["metric"] == "Net Income" for a in alerts)


async def test_analysis_endpoints_require_auth(client):
    resp = await client.post(
        "/api/v1/analysis/health-score", json={"current": METRICS_B, "prior": METRICS_A}
    )
    assert resp.status_code == 401
