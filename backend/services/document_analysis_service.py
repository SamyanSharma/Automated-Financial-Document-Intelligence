from sqlalchemy.orm import Session

from services.retrieval_service import search_similar_chunks
from services.financial_extraction_service import extract_financial_metrics
from services.financial_metric_service import save_financial_metrics
from services.financial_parser_service import normalize_financial_metrics



def analyze_document(
    db: Session,
    document_id: int,
    question: str
):

    # Step 1:
    # Retrieve important document chunks

    chunks = search_similar_chunks(
        db=db,
        query=question,
        top_k=5
    )


    context = "\n\n".join(
        [
            chunk["text"]
            for chunk in chunks
        ]
    )


    # Step 2:
    # Extract financial values

    metrics = extract_financial_metrics(
    context
)

    metrics = normalize_financial_metrics(
        metrics
    )


    # Step 3:
    # Save metrics in database

    saved_metrics = save_financial_metrics(
        db=db,
        document_id=document_id,
        metrics=metrics
    )


    return saved_metrics