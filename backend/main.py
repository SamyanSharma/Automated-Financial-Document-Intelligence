from fastapi import FastAPI

from routers import documents
from routers import companies
from routers import analysis
from routers import rag


app = FastAPI(
    title="Automated Financial Document Intelligence",
    description="AI-powered financial document analysis API",
    version="1.0.0"
)


app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    companies.router,
    prefix="/api/v1",
    tags=["Companies"]
)

app.include_router(
    analysis.router
)

app.include_router(
    rag.router
)


@app.get("/")
def root():
    return {
        "message": "Automated Financial Document Intelligence API is running"
    }