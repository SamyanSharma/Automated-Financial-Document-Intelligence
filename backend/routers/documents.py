"""
/api/v1/documents endpoints: upload, status, chunks.

Design:
- POST /upload validates the file is a PDF and within the size limit,
  saves it to disk, creates a Document row (status=processing), then
  kicks off extraction+chunking as a FastAPI BackgroundTask so the
  client gets an immediate {document_id, status} response instead of
  blocking on PDF parsing. The client is expected to poll the status
  endpoint (per Member 3's frontend spec).
- The background task (`_process_document`) does extraction -> chunking
  -> DB persistence in one transaction, with rollback + status="failed"
  + error_message on any failure, so nothing is left half-written.
- GET /{id}/status and GET /{id}/chunks both verify the document belongs
  to the requesting user (404, not 403, to avoid leaking existence of
  other users' documents).
"""
from __future__ import annotations

import logging
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import AsyncSessionLocal, get_db
from models.document import Document, DocumentChunk, DocumentStatus
from models.user import User
from routers.auth import get_current_user
from schemas.document import (
    DocumentChunkOut,
    DocumentChunksOut,
    DocumentStatusOut,
    DocumentUploadOut,
)
from services.chunk_service import chunk_pages
from services.pdf_service import PDFExtractionError, extract_text_by_page

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
settings = get_settings()


async def _process_document(document_id: str, storage_path: str) -> None:
    """
    Background task: extract text, chunk it, persist chunks. Uses its own
    DB session since the request's session is closed by the time this runs.
    """
    async with AsyncSessionLocal() as db:
        document = await db.get(Document, document_id)
        if document is None:
            logger.error("Document %s vanished before processing", document_id)
            return

        try:
            pages = extract_text_by_page(storage_path)
            chunks = chunk_pages(
                pages,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )

            for c in chunks:
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        text=c.text,
                        page_number=c.page_number,
                        sequence=c.sequence,
                        char_start=c.char_start,
                        char_end=c.char_end,
                    )
                )

            document.status = DocumentStatus.COMPLETED
            document.total_pages = len(pages)
            document.total_chunks = len(chunks)
            document.error_message = None

            await db.commit()
            logger.info(
                "Processed document %s: %d pages, %d chunks",
                document_id, len(pages), len(chunks),
            )

        except PDFExtractionError as exc:
            await db.rollback()
            document = await db.get(Document, document_id)
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)
            await db.commit()
            logger.warning("Extraction failed for document %s: %s", document_id, exc)

        except Exception as exc:
            await db.rollback()
            document = await db.get(Document, document_id)
            document.status = DocumentStatus.FAILED
            document.error_message = "Internal error during processing"
            await db.commit()
            logger.exception("Unexpected error processing document %s: %s", document_id, exc)


@router.post("/upload", response_model=DocumentUploadOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadOut:
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    os.makedirs(settings.upload_dir, exist_ok=True)
    document_id = str(uuid.uuid4())
    safe_name = f"{document_id}.pdf"
    storage_path = os.path.join(settings.upload_dir, safe_name)

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    size = 0
    try:
        with open(storage_path, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds max size of {settings.max_upload_size_mb}MB",
                    )
                out.write(chunk)
    except HTTPException:
        if os.path.exists(storage_path):
            os.remove(storage_path)
        raise
    except Exception:
        logger.exception("Failed to save uploaded file")
        if os.path.exists(storage_path):
            os.remove(storage_path)
        raise HTTPException(status_code=500, detail="Could not save uploaded file")

    if size == 0:
        os.remove(storage_path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    document = Document(
        id=document_id,
        user_id=current_user.id,
        filename=file.filename,
        storage_path=storage_path,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    background_tasks.add_task(_process_document, document.id, storage_path)
    logger.info("Document %s uploaded by user %s, processing started", document.id, current_user.id)

    return DocumentUploadOut(document_id=document.id, status=document.status)


async def _get_owned_document(document_id: str, db: AsyncSession, current_user: User) -> Document:
    document = await db.get(Document, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/status", response_model=DocumentStatusOut)
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentStatusOut:
    document = await _get_owned_document(document_id, db, current_user)
    return DocumentStatusOut(
        document_id=document.id,
        status=document.status,
        total_pages=document.total_pages,
        total_chunks=document.total_chunks,
        error_message=document.error_message,
    )


@router.get("/{document_id}/chunks", response_model=DocumentChunksOut)
async def get_document_chunks(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentChunksOut:
    document = await _get_owned_document(document_id, db, current_user)

    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Document is not ready yet (status={document.status.value})",
        )

    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.sequence)
    )
    chunks = result.scalars().all()

    return DocumentChunksOut(
        document_id=document.id,
        total_chunks=len(chunks),
        chunks=[DocumentChunkOut.model_validate(c) for c in chunks],
    )
