from fastapi import APIRouter, Request

from app.api.proxy import proxy_get, proxy_post
from app.schemas import (
    CoordinatesCreate,
    PointCoordinatesResponse,
    PointCreate,
    PointFilters,
    PointResponse,
)

router = APIRouter(prefix="/points", tags=["points"])


@router.get("/filters", response_model=PointFilters)
async def point_filters(request: Request):
    """Get type hierarchy filter options for points."""
    return await proxy_get(request.app.state.db_client, "points/filters")


@router.get("/{point_id}", response_model=PointResponse)
async def get_point(point_id: int, request: Request):
    """Get full point details with all relations."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}",
        params={"extended": "true"},
    )


@router.get("/{point_id}/coordinates", response_model=PointCoordinatesResponse)
async def get_point_coordinates(point_id: int, request: Request):
    """Get all coordinates for a point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/coordinates",
    )


@router.get("/{point_id}/notes")
async def get_point_notes(point_id: int, request: Request):
    """Get all notes associated with a point."""
    return await proxy_get(
        request.app.state.db_client,
        f"points/{point_id}/notes",
    )


@router.post("/", response_model=PointResponse, status_code=201)
async def create_point(body: PointCreate, request: Request):
    """Create a new point."""
    return await proxy_post(
        request.app.state.db_client,
        "points/",
        body.model_dump(),
    )


@router.post("/{point_id}/coordinates", status_code=201)
async def add_point_coordinates(
    point_id: int, body: CoordinatesCreate, request: Request
):
    """Add coordinates to an existing point."""
    return await proxy_post(
        request.app.state.db_client,
        f"points/{point_id}/coordinates",
        body.model_dump(),
    )
