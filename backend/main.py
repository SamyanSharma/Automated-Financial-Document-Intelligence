from fastapi import FastAPI

import models
from database import engine

from routers import documents
from routers.analysis import router as analysis_router


models.Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Financial Document Intelligence API"
)


app.include_router(
    analysis_router
)


app.include_router(
    documents.router,
    prefix="/documents"
)


@app.get("/")
def home():

    return {
        "message":
        "Financial AI Backend Running"
    }