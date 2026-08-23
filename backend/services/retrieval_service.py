import math

from sqlalchemy.orm import Session
from models import DocumentChunk
from services.embedding_service import generate_embedding


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float]
) -> float:

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5
):
    query_embedding = generate_embedding(query)

    chunks = db.query(DocumentChunk).all()

    results = []

    for chunk in chunks:

        if not chunk.embedding:
            continue

        similarity = cosine_similarity(
            query_embedding,
            chunk.embedding
        )

        results.append(
            {
                "chunk_id": chunk.id,
                "filing_id": chunk.filing_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "similarity": similarity
            }
        )

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:top_k]