from sqlalchemy.orm import Session
from models import DocumentChunk
from services.embedding_service import generate_embedding


def save_chunks(
    db: Session,
    filing_id: int,
    chunks: list[str]
):
    saved_chunks = []

    try:
        for index, chunk in enumerate(chunks):

            embedding = generate_embedding(chunk)

            document_chunk = DocumentChunk(
                filing_id=filing_id,
                chunk_index=index,
                text=chunk,
                embedding=embedding
            )

            db.add(document_chunk)
            saved_chunks.append(document_chunk)

        db.commit()

        return saved_chunks

    except Exception:
        db.rollback()
        raise