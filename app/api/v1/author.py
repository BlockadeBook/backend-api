from fastapi import APIRouter, Depends, Request

from app.api.cache import cached_proxy_get
from app.api.proxy import proxy_get, proxy_post
from app.auth.decorators import admin_required
from app.schemas import AuthorCreate, AuthorFilters, AuthorResponse, AuthorShort

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[AuthorShort])
async def list_authors(request: Request):
    """List all authors (short read, no relations)."""
    return await proxy_get(
        request.app.state.db_client,
        "authors/",
        params={"extended": "false"},
    )


@router.get("/filters", response_model=AuthorFilters)
async def author_filters(request: Request):
    """Get all filter options for authors."""
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "authors/filters")


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(author_id: int, request: Request):
    """Get full author details with all relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"authors/{author_id}",
        params={"extended": "true"},
    )


@router.post("/", response_model=AuthorResponse, status_code=201, dependencies=[Depends(admin_required)])
async def create_author(body: AuthorCreate, request: Request):
    """Create a new author."""
    return await proxy_post(
        request.app.state.db_client,
        "authors/",
        body.model_dump(),
    )
