from database import SessionLocal
from services.chunk_service import split_text
from services.chunk_storage_service import save_chunks


text = """
Apple Inc. reported total net sales of approximately 394.3 billion dollars
for the fiscal year. Products contributed a significant portion of total
revenue, while Services revenue continued to grow during the year.

The company reported total assets of approximately 352.6 billion dollars.
Cash and cash equivalents, marketable securities, accounts receivable and
inventory represented important components of current assets.

Apple reported total liabilities of approximately 290.0 billion dollars.
Long-term debt and other non-current liabilities represented a substantial
portion of the company's obligations.

The company's operating income increased during the fiscal year as revenue
grew and operating expenses were managed. Gross margin was affected by
product mix, foreign exchange movements and costs associated with products.

Apple generated substantial operating cash flow during the year. Capital
expenditures were used primarily for manufacturing facilities, equipment,
data centers and other infrastructure.

The company also returned capital to shareholders through dividends and
share repurchases. These activities affected the company's financing cash
flows and shareholders' equity.
"""


chunks = split_text(text)

print("Chunks generated:", len(chunks))

db = SessionLocal()

try:

    saved = save_chunks(
        db=db,
        filing_id=1,
        chunks=chunks
    )

    print("Chunks saved:", len(saved))

finally:

    db.close()