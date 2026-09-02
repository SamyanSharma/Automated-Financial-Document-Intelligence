from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import FinancialMetric


router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Companies"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_companies(
    db: Session = Depends(get_db)
):
    companies = (
        db.query(FinancialMetric.company_name)
        .filter(
            FinancialMetric.company_name.isnot(None)
        )
        .distinct()
        .order_by(FinancialMetric.company_name)
        .all()
    )

    return {
        "companies": [
            company[0]
            for company in companies
        ]
    }