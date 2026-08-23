from fastapi import APIRouter, Depends
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
    company_name:str,
    db:Session = Depends(get_db)
):


    history = get_company_history(
        db,
        company_name.strip()
    )


    if not history:
        return {
            "error":
            "No financial data found"
        }



    latest = history[-1]

    previous = history[-2]


    financial_data = {

        "revenue_current":
        latest["revenue"],

        "revenue_previous":
        previous["revenue"],


        "debt_current":
        latest["debt"],

        "debt_previous":
        previous["debt"],


        "liability_current":
        latest["liabilities"],

        "liability_previous":
        previous["liabilities"],


        "revenue_history":
        [
            item["revenue"]
            for item in history
        ]

    }



    report = generate_financial_report(

        company_name,

        history,

        financial_data

    )


    return report