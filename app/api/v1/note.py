from fastapi import APIRouter, Request

from app.api.proxy import proxy_get, proxy_post
from app.schemas import NoteCreate, NoteDetailed, NoteFilters, NoteResponse, NoteShort, TagCreate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/filters", response_model=NoteFilters)
async def note_filters(request: Request):
    """Get all filter options for notes."""
    return await proxy_get(request.app.state.db_client, "notes/filters")


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


@router.get("/by-point/{point_id}", response_model=list[NoteShort])
async def notes_by_point(point_id: int, request: Request):
    """List short notes for a specific point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/notes",
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
