from fastapi import APIRouter, Request

from app.api.proxy import proxy_get
from app.schemas import DiaryResponse, NoteResponse

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.get("/")
async def list_diaries(request: Request):
    """List all diaries with author info."""
    return await proxy_get(
        request.app.state.db_client,
        "diaries/",
        params={"extended": "true"},
    )


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(diary_id: int, request: Request):
    """Get diary by ID with author info."""
    return await proxy_get(
        request.app.state.db_client,
        f"diaries/{diary_id}",
        params={"extended": "true"},
    )


@router.get("/{diary_id}/notes", response_model=list[NoteResponse])
async def get_diary_notes(diary_id: int, request: Request):
    """Get all notes for a diary."""
    return await proxy_get(
        request.app.state.db_client,
        f"diaries/{diary_id}/notes",
        params={"extended": "true"},
    )
