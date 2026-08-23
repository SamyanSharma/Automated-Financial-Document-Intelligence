from database import SessionLocal
from models import FinancialMetric


db = SessionLocal()


records = [

    FinancialMetric(
        document_id=1,
        company_name="Apple Inc.",
        financial_year="2020",
        revenue=274,
        total_assets=323,
        total_liabilities=258,
        debt=98
    ),


    FinancialMetric(
        document_id=2,
        company_name="Apple Inc.",
        financial_year="2021",
        revenue=365,
        total_assets=351,
        total_liabilities=287,
        debt=109
    ),


    FinancialMetric(
        document_id=3,
        company_name="Apple Inc.",
        financial_year="2022",
        revenue=394,
        total_assets=352,
        total_liabilities=302,
        debt=111
    ),


    FinancialMetric(
        document_id=4,
        company_name="Apple Inc.",
        financial_year="2023",
        revenue=383,
        total_assets=352,
        total_liabilities=290,
        debt=110
    )

]


db.add_all(records)

db.commit()

print("History data inserted")

db.close()