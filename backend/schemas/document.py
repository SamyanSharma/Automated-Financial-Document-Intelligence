"""
Pydantic v2 schemas for document upload/status/chunks responses.

DocumentChunkOut is deliberately the exact shape the AI module (Member 2)
needs: chunk text + page number + sequence, so retriever.py / embedding_service.py
can consume GET /documents/{id}/chunks with no extra transformation.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.document import DocumentStatus


class DocumentUploadOut(BaseModel):
    """Response for POST /api/v1/documents/upload"""
    document_id: str
    status: DocumentStatus


class DocumentStatusOut(BaseModel):
    """Response for GET /api/v1/documents/{id}/status"""
    model_config = ConfigDict(from_attributes=True)

    document_id: str = ""
    status: DocumentStatus
    total_pages: int | None = None
    total_chunks: int | None = None
    error_message: str | None = None


class DocumentChunkOut(BaseModel):
    """A single chunk, shaped for the AI module to consume directly."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    page_number: int
    sequence: int


class DocumentChunksOut(BaseModel):
    """Response for GET /api/v1/documents/{id}/chunks"""
    document_id: str
    total_chunks: int
    chunks: list[DocumentChunkOut]


class DocumentOut(BaseModel):
    """General document metadata shape."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: DocumentStatus
    total_pages: int | None
    total_chunks: int | None
    uploaded_at: datetime
