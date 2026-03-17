from fastapi import APIRouter

from app.api.author.router import router as author_router

api_router = APIRouter()

api_router.include_router(author_router)
