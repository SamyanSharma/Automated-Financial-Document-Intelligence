import asyncio
import os

import pytest

pytestmark = pytest.mark.asyncio

TINY_PDF_PATH = os.path.join(os.path.dirname(__file__), "tiny.pdf")


async def _upload_tiny_pdf(client, auth_headers):
    with open(TINY_PDF_PATH, "rb") as f:
        resp = await client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("tiny.pdf", f, "application/pdf")},
        )
    return resp


async def _wait_for_status(client, auth_headers, document_id, target_statuses, timeout=5.0):
    """Poll the status endpoint until it reaches one of target_statuses or times out."""
    elapsed = 0.0
    interval = 0.1
    while elapsed < timeout:
        resp = await client.get(f"/api/v1/documents/{document_id}/status", headers=auth_headers)
        if resp.json().get("status") in target_statuses:
            return resp
        await asyncio.sleep(interval)
        elapsed += interval
    return resp


async def test_upload_requires_auth(client):
    with open(TINY_PDF_PATH, "rb") as f:
        resp = await client.post(
            "/api/v1/documents/upload", files={"file": ("tiny.pdf", f, "application/pdf")}
        )
    assert resp.status_code == 401


async def test_upload_rejects_non_pdf(client, auth_headers):
    resp = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("notes.txt", b"just some text", "text/plain")},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


async def test_upload_rejects_empty_file(client, auth_headers):
    resp = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert resp.status_code == 400


async def test_upload_returns_processing_status(client, auth_headers):
    resp = await _upload_tiny_pdf(client, auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "processing"
    assert "document_id" in body


async def test_full_pipeline_reaches_completed_with_chunks(client, auth_headers):
    upload_resp = await _upload_tiny_pdf(client, auth_headers)
    document_id = upload_resp.json()["document_id"]

    status_resp = await _wait_for_status(client, auth_headers, document_id, {"completed", "failed"})
    body = status_resp.json()
    assert body["status"] == "completed"
    assert body["total_pages"] == 1
    assert body["total_chunks"] >= 1

    chunks_resp = await client.get(f"/api/v1/documents/{document_id}/chunks", headers=auth_headers)
    assert chunks_resp.status_code == 200
    chunks_body = chunks_resp.json()
    assert chunks_body["total_chunks"] == body["total_chunks"]
    assert len(chunks_body["chunks"]) == chunks_body["total_chunks"]
    first_chunk = chunks_body["chunks"][0]
    assert "revenue" in first_chunk["text"].lower()
    assert first_chunk["page_number"] == 1
    assert first_chunk["sequence"] == 0


async def test_corrupt_pdf_marks_document_failed(client, auth_headers):
    resp = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("corrupt.pdf", b"%PDF-1.4 not a real pdf body", "application/pdf")},
    )
    document_id = resp.json()["document_id"]

    status_resp = await _wait_for_status(client, auth_headers, document_id, {"completed", "failed"})
    body = status_resp.json()
    assert body["status"] == "failed"
    assert body["error_message"] is not None


async def test_chunks_not_available_before_processing_completes(client, auth_headers):
    upload_resp = await _upload_tiny_pdf(client, auth_headers)
    document_id = upload_resp.json()["document_id"]
    # Immediately request chunks, before the background task has necessarily finished.
    # Either 409 (still processing) or 200 (finished fast) is acceptable; assert no crash.
    resp = await client.get(f"/api/v1/documents/{document_id}/chunks", headers=auth_headers)
    assert resp.status_code in (200, 409)


async def test_status_404_for_unknown_document(client, auth_headers):
    resp = await client.get("/api/v1/documents/does-not-exist/status", headers=auth_headers)
    assert resp.status_code == 404


async def test_status_404_for_other_users_document(client, auth_headers):
    upload_resp = await _upload_tiny_pdf(client, auth_headers)
    document_id = upload_resp.json()["document_id"]

    await client.post("/auth/register", json={"email": "other@example.com", "password": "password123"})
    login = await client.post("/auth/login", json={"email": "other@example.com", "password": "password123"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.get(f"/api/v1/documents/{document_id}/status", headers=other_headers)
    assert resp.status_code == 404
