from database import SessionLocal
from services.document_analysis_service import analyze_document



db = SessionLocal()


try:

    result = analyze_document(

        db=db,

        document_id=1,

        question=
        "Extract revenue, assets, liabilities, debt and cash flow from this financial report"

    )


    print("Saved metric ID:")
    print(result.id)


finally:

    db.close()