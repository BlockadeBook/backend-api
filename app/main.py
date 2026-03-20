import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.v1.author import router as author_router
from app.api.v1.note import router as note_router
from app.api.v1.loader import router as loader_router
from app.api.v1.point import router as point_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "http://127.0.0.1:8080")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create async httpx client on startup, close on shutdown."""
    app.state.db_client = httpx.AsyncClient(base_url=DATABASE_URL)
    app.state.filter_cache: dict[str, dict] = {}
    yield
    await app.state.db_client.aclose()


app = FastAPI(
    title="backend-api",
    description="API gateway that proxies requests to database-core",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(author_router, prefix="/api/v1")
app.include_router(note_router, prefix="/api/v1")
app.include_router(loader_router, prefix="/api/v1")
app.include_router(point_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
