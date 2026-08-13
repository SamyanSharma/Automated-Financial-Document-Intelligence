"""
Integration router for the AI module (Member 2's scope).

Not in the original directory listing for backend/ai/ (that lists only
service files, no router — routers/ belongs to Member 1's ownership per
spec). Added here, not by editing Member 1's routers/documents.py, so
each member's committed files stay untouched by the other. This mirrors
how Member 1 added security.py: a necessary integration file the spec's
file list didn't enumerate but the working system needs.

Endpoints:
- POST /api/v1/documents/{id}/embed   - embed a completed document's chunks
- POST /api/v1/chat                   - RAG Q&A (matches Member 3's spec exactly)
- POST /api/v1/analysis/health-score  - Algorithm 1
- POST /api/v1/analysis/compare       - Algorithm 2
- POST /api/v1/analysis/anomalies     - Algorithm 3

Embed/chat re-use Member 1's `_get_owned_document` and `get_current_user`
so document ownership/auth rules are enforced identically to the ingestion
endpoints (404 for someone else's document, 401 for no token) — imported,
not duplicated.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.chat_service import answer_question
from ai.comparison_engine import compare_reports
from ai.embedding_service import get_embedder
from ai.risk_engine import compute_health_score, detect_anomalies
from ai.schemas import (
    AnomalyDetectionRequest,
    AnomalyDetectionResult,
    ChatRequest,
    ChatResponse,
    ComparisonRequest,
    ComparisonResult,
    EmbedDocumentResponse,
    HealthScoreRequest,
    HealthScoreResult,
)
from ai.vector_store import get_vector_store
from database import get_db
from models.document import DocumentChunk, DocumentStatus
from models.user import User
from routers.auth import get_current_user
from routers.documents import _get_owned_document

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["ai"])


@router.post("/documents/{document_id}/embed", response_model=EmbedDocumentResponse)
async def embed_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmbedDocumentResponse:
    document = await _get_owned_document(document_id, db, current_user)

    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Document is not ready to embed yet (status={document.status.value})",
        )

    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.sequence)
    )
    chunks = result.scalars().all()

    if not chunks:
        raise HTTPException(status_code=400, detail="Document has no chunks to embed")

    embedder = get_embedder()
    texts = [c.text for c in chunks]
    embeddings = embedder.embed_texts(texts)

    store = get_vector_store()
    count = store.add_chunks(
        chunk_ids=[c.id for c in chunks],
        texts=texts,
        embeddings=embeddings,
        document_id=document.id,
        page_numbers=[c.page_number for c in chunks],
        sequences=[c.sequence for c in chunks],
    )

    logger.info("Embedded %d chunks for document %s (user %s)", count, document.id, current_user.id)
    return EmbedDocumentResponse(document_id=document.id, chunks_embedded=count)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    # Ownership check before touching the vector store, so a user can't
    # probe another user's embedded content via the chat endpoint.
    await _get_owned_document(payload.document_id, db, current_user)

    return answer_question(
        document_id=payload.document_id,
        question=payload.question,
        top_k=payload.top_k,
    )


@router.post("/analysis/health-score", response_model=HealthScoreResult)
async def health_score(
    payload: HealthScoreRequest,
    current_user: User = Depends(get_current_user),
) -> HealthScoreResult:
    return compute_health_score(payload.current, payload.prior)


@router.post("/analysis/compare", response_model=ComparisonResult)
async def compare(
    payload: ComparisonRequest,
    current_user: User = Depends(get_current_user),
) -> ComparisonResult:
    return compare_reports(payload.current, payload.prior)


@router.post("/analysis/anomalies", response_model=AnomalyDetectionResult)
async def anomalies(
    payload: AnomalyDetectionRequest,
    current_user: User = Depends(get_current_user),
) -> AnomalyDetectionResult:
    return detect_anomalies(payload.current, payload.prior, payload.history)
