from database import SessionLocal
from services.financial_history_service import get_company_history



db = SessionLocal()


history = get_company_history(
    db,
    "Apple Inc."
)


for item in history:
    print(item)


db.close()