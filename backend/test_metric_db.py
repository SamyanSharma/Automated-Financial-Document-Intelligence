from database import SessionLocal
from services.financial_metric_service import save_financial_metrics



db = SessionLocal()


metrics = {

    "company_name":"Apple",

    "financial_year":"2024",

    "revenue":394.3,

    "total_assets":352.6,

    "total_liabilities":290,

    "debt":106,

    "cash_flow":110

}



try:

    result = save_financial_metrics(
        db=db,
        document_id=1,
        metrics=metrics
    )


    print(
        "Saved:",
        result.id
    )


finally:

    db.close()