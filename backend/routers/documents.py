from fastapi import APIRouter, UploadFile, File
import shutil
from database import SessionLocal
from models import Filing
from services.pdf_service import extract_text



router = APIRouter()


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(path)

    db = SessionLocal()

    new_filing = Filing(
        company_name="Unknown",
        filename=file.filename,
        file_path=path,
        extracted_text=extracted_text
    )

    db.add(new_filing)
    db.commit()
    db.refresh(new_filing)
    db.close()

    return {
        "message": "File uploaded successfully",
        "id": new_filing.id,
        "filename": new_filing.filename
    }