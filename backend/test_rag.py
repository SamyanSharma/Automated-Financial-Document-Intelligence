from database import SessionLocal
from services.rag_service import answer_question

db = SessionLocal()

try:

    question = "What was the company's revenue?"

    result = answer_question(
        db=db,
        question=question,
        top_k=3
    )

    print("\n==============================")
    print("ANSWER")
    print("==============================")

    print(result["answer"])

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for source in result["sources"]:
        print(source)

finally:

    db.close()