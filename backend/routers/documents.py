from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

from database import SessionLocal
from models import Filing, FinancialMetric

from services.pdf_service import extract_text
from services.financial_extraction_service import extract_financial_metrics


router = APIRouter()


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...)
):
    # --------------------------------------------------
    # Validate file
    # --------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # --------------------------------------------------
    # Save PDF
    # --------------------------------------------------

    path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    try:

        with open(path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # --------------------------------------------------
        # Extract PDF text
        # --------------------------------------------------

        extracted_text = extract_text(path)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # --------------------------------------------------
        # Create database session
        # --------------------------------------------------

        db = SessionLocal()

        try:

            # --------------------------------------------------
            # Create Filing
            # --------------------------------------------------

            new_filing = Filing(
                company_name="Unknown",
                filename=file.filename,
                file_path=path,
                extracted_text=extracted_text
            )

            db.add(new_filing)
            db.commit()
            db.refresh(new_filing)

            # --------------------------------------------------
            # Financial extraction
            # --------------------------------------------------

            metrics = extract_financial_metrics(
                extracted_text
            )

            print("EXTRACTED METRICS:")
            print(metrics)

            # --------------------------------------------------
            # Update Filing company name
            # --------------------------------------------------

            company_name = metrics.get(
                "company_name"
            )

            if company_name:

                new_filing.company_name = company_name

                db.commit()
                db.refresh(new_filing)

            # --------------------------------------------------
            # Save FinancialMetric
            # --------------------------------------------------

            financial_metric = FinancialMetric(

                document_id=new_filing.id,

                company_name=company_name
                or "Unknown",

                financial_year=metrics.get(
                    "financial_year"
                ),

                revenue=metrics.get(
                    "revenue"
                ),

                total_assets=metrics.get(
                    "total_assets"
                ),

                total_liabilities=metrics.get(
                    "total_liabilities"
                ),

                debt=metrics.get(
                    "debt"
                ),

                cash_flow=metrics.get(
                    "cash_flow"
                )
            )

            db.add(financial_metric)

            db.commit()
            db.refresh(financial_metric)

            # --------------------------------------------------
            # Response
            # --------------------------------------------------

            return {
                "message": "Document processed successfully",

                "document": {
                    "id": new_filing.id,
                    "filename": new_filing.filename,
                    "company_name": new_filing.company_name
                },

                "financial_metrics": {
                    "id": financial_metric.id,
                    "company_name": financial_metric.company_name,
                    "financial_year": financial_metric.financial_year,
                    "revenue": financial_metric.revenue,
                    "total_assets": financial_metric.total_assets,
                    "total_liabilities": financial_metric.total_liabilities,
                    "debt": financial_metric.debt,
                    "cash_flow": financial_metric.cash_flow
                }
            }

        finally:

            db.close()

    except HTTPException:
        raise

    except Exception as e:

        print("UPLOAD ERROR:")
        print(e)

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )