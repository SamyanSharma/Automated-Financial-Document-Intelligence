from sqlalchemy.orm import Session

from models import FinancialMetric



def save_financial_metrics(
    db: Session,
    document_id: int,
    metrics: dict
):

    financial_record = FinancialMetric(

        document_id=document_id,

        company_name=
        metrics.get("company_name"),


        financial_year=
        metrics.get("financial_year"),


        revenue=
        metrics.get("revenue"),


        total_assets=
        metrics.get("total_assets"),


        total_liabilities=
        metrics.get("total_liabilities"),


        debt=
        metrics.get("debt"),


        cash_flow=
        metrics.get("cash_flow")
    )


    db.add(financial_record)

    db.commit()

    db.refresh(financial_record)


    return financial_record