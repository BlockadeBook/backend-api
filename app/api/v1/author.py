from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.cache import cached_proxy_get
from app.api.filter import filter_response
from app.api.proxy import proxy_get, proxy_post
from app.schemas import AuthorCreate, AuthorFilters, AuthorResponse, AuthorShort

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=list[AuthorResponse])
async def list_authors(
    request: Request,
    family_status_id: Optional[int] = Query(default=None),
    social_class_id: Optional[list[int]] = Query(default=None),
    nationality_id: Optional[list[int]] = Query(default=None),
    religion_id: Optional[list[int]] = Query(default=None),
    education_id: Optional[list[int]] = Query(default=None),
    occupation_id: Optional[list[int]] = Query(default=None),
    political_party_id: Optional[list[int]] = Query(default=None),
    card_id: Optional[list[int]] = Query(default=None),
):
    """List authors with optional filtering."""
    data = await proxy_get(
        request.app.state.db_client,
        "authors/",
        params={"extended": "true"},
    )
    filters = {
        "family_status_id": [family_status_id] if family_status_id else [],
        "social_classes": social_class_id or [],
        "nationalities": nationality_id or [],
        "religions": religion_id or [],
        "education": education_id or [],
        "occupation": occupation_id or [],
        "political_parties": political_party_id or [],
        "cards": card_id or [],
    }
    return filter_response(
        data,
        filters,
        list_fields={"social_classes", "nationalities", "religions", "education", "occupation", "political_parties", "cards"},
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


@router.post("/", response_model=AuthorResponse, status_code=201)
async def create_author(body: AuthorCreate, request: Request):
    """Create a new author."""
    return await proxy_post(
        request.app.state.db_client,
        "authors/",
        body.model_dump(),
    )