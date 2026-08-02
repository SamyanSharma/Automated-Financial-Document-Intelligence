from fastapi import FastAPI
import models

from database import engine
from routers import documents


models.Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Financial Document Intelligence API"
)


app.include_router(
    documents.router,
    prefix="/documents"
)


@app.get("/")
def home():
    return {
        "message":"Financial AI Backend Running"
    }