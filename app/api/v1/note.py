from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.cache import cached_proxy_get
from app.api.filter import filter_response
from app.api.proxy import proxy_get, proxy_post
from app.schemas import NoteCreate, NoteDetailed, NoteFilters, NoteResponse, NoteShort, TagCreate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/filters", response_model=NoteFilters)
async def note_filters(request: Request):
    """Get all filter options for notes."""
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "notes/filters")


@router.post("/tags", status_code=201)
async def create_tag(body: TagCreate, request: Request):
    """Create a new tag."""
    return await proxy_post(
        request.app.state.db_client,
        "notes/tags",
        body.model_dump(),
    )


@router.get("/detailed/{note_id}", response_model=NoteDetailed)
async def detailed_note(note_id: int, request: Request):
    """Get note with full author and point details."""
    return await proxy_get(request.app.state.db_client, f"notes/detailed/{note_id}")


@router.get("/by-point/{point_id}")
async def notes_by_point(point_id: int, request: Request):
    """List full notes for a specific point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/notes",
        params={"extended": "true"},
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, request: Request):
    """Get full note details with relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"notes/{note_id}",
        params={"extended": "true"},
    )


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(body: NoteCreate, request: Request):
    """Create a new note."""
    return await proxy_post(
        request.app.state.db_client,
        "notes/",
        body.model_dump(),
    )


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    request: Request,
    tag_id: Optional[list[int]] = Query(default=None),
    note_type_id: Optional[list[int]] = Query(default=None),
    temporality_id: Optional[list[int]] = Query(default=None),
):
    """List notes with optional filtering."""
    data = await proxy_get(
        request.app.state.db_client,
        "notes/",
        params={"extended": "true"},
    )
    filters = {
        "tags": tag_id or [],
        "note_type_id": note_type_id or [],
        "temporality_id": temporality_id or [],
    }
    return filter_response(data, filters, list_fields={"tags"})