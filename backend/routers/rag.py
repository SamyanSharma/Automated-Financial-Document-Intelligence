from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RAGRequest(BaseModel):
    question: str
    company_name: str | None = None


@router.post("/rag/ask")
def ask_question(request: RAGRequest):

    # Existing retrieval + Gemini logic will be connected here.

    return {
        "question": request.question,
        "answer": "",
        "sources": []
    }