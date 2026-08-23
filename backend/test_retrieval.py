from database import SessionLocal
from services.retrieval_service import search_similar_chunks


queries = [
    "What was the company's revenue?",
    "What were the company's total liabilities?",
    "How much operating cash flow did the company generate?",
    "What did the company do with its capital?"
]


db = SessionLocal()

try:

    for query in queries:

        print("\n\n====================================")
        print("QUESTION:", query)
        print("====================================")

        results = search_similar_chunks(
            db=db,
            query=query,
            top_k=2
        )

        for result in results:

            print("\nChunk ID:", result["chunk_id"])
            print("Similarity:", round(result["similarity"], 4))
            print("Text:")
            print(result["text"][:500])

finally:

    db.close()