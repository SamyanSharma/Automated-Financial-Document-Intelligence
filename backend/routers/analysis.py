from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from services.financial_history_service import get_company_history
from services.report_generator_service import generate_financial_report


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/company/{company_name}")
def analyze_company(
    company_name: str,
    db: Session = Depends(get_db)
):
    company_name = company_name.strip()

    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Company name cannot be empty"
        )

    history = get_company_history(
        db,
        company_name
    )

    # No financial records
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No financial data found for {company_name}"
        )

    # At least two years are required for
    # comparison / YoY / risk analysis.
    if len(history) < 2:
        raise HTTPException(
            status_code=400,
            detail=(
                f"At least two financial records are required "
                f"to analyze {company_name}. "
                f"Currently found {len(history)} record."
            )
        )

    latest = history[-1]
    previous = history[-2]

    financial_data = {
        "revenue_current": latest.get("revenue"),
        "revenue_previous": previous.get("revenue"),

        "debt_current": latest.get("debt"),
        "debt_previous": previous.get("debt"),

        "liability_current": latest.get("liabilities"),
        "liability_previous": previous.get("liabilities"),

        "revenue_history": [
            item.get("revenue")
            for item in history
            if item.get("revenue") is not None
        ]
    }

    report = generate_financial_report(
        company_name,
        history,
        financial_data
    )

    return report

@router.get("/company/{company_name}/history")
def company_history(
    company_name: str,
    db: Session = Depends(get_db)
):
    company_name = company_name.strip()

    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Company name cannot be empty"
        )

    history = get_company_history(
        db,
        company_name
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No financial history found for {company_name}"
        )

    return {
        "company": company_name,
        "history": history
    }