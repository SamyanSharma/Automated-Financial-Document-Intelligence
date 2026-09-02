from sqlalchemy.orm import Session

from models import FinancialMetric


def get_company_history(
    db: Session,
    company_name: str
):
    records = (
        db.query(FinancialMetric)
        .filter(
            FinancialMetric.company_name.ilike(
                company_name.strip()
            )
        )
        .all()
    )

    history = []

    for record in records:

        history.append({
            "year": record.financial_year,
            "revenue": record.revenue,
            "assets": record.total_assets,
            "liabilities": record.total_liabilities,
            "debt": record.debt,
            "cash_flow": record.cash_flow
        })

    # for record in records:

    #     print(
    #         "DB RECORD:",
    #         "id =", record.id,
    #         "company =", record.company_name,
    #         "year =", record.financial_year,
    #         "revenue =", record.revenue
    #     )

    #     history.append({
    #         "year": record.financial_year,
    #         "revenue": record.revenue,
    #         "assets": record.total_assets,
    #         "liabilities": record.total_liabilities,
    #         "debt": record.debt,
    #         "cash_flow": record.cash_flow
    #     })

    def year_sort_key(item):
        year = item.get("year")

        try:
            return (0, int(year))
        except (TypeError, ValueError):
            return (1, 0)

    history.sort(key=year_sort_key)

    return history