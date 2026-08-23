from sqlalchemy.orm import Session

from services.retrieval_service import search_similar_chunks
from services.llm_service import generate_answer


def answer_question(
    db: Session,
    question: str,
    top_k: int = 5
):

    results = search_similar_chunks(
        db=db,
        query=question,
        top_k=top_k
    )

    if not results:
        return {
            "answer": "I could not find relevant information in the documents.",
            "sources": []
        }

    context_parts = []

    sources = []

    for result in results:

        context_parts.append(
            f"""
SOURCE CHUNK {result['chunk_id']}
Similarity: {result['similarity']}

{result['text']}
"""
        )

        sources.append(
            {
                "chunk_id": result["chunk_id"],
                "similarity": result["similarity"]
            }
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question=question,
        context=context
    )

    return {
        "answer": answer,
        "sources": sources
    }