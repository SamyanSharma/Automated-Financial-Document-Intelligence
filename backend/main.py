"""
FastAPI entrypoint.

Logging design: configured once here at startup using the standard
`logging` module (per spec — no third-party logging lib). Every module
in this codebase does `logger = logging.getLogger(__name__)` and calls
logger.info/warning/exception, so this basicConfig call controls format
and level for the whole app. In production, `debug=False` -> INFO level;
in dev, DEBUG level for verbose SQL/trace output.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db
import models  # noqa: F401 - ensures all models are registered on Base.metadata
from routers import auth, documents

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s (env=%s)", settings.app_name, settings.environment)
    # Dev/test convenience only — real deployments manage schema via Alembic.
    if settings.database_url.startswith("sqlite"):
        await init_db()
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(documents.router)
