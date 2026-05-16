# Query Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add post-fetch query-parameter filtering to list endpoints (notes, points, authors).

**Architecture:** Gateway fetches full collection from database-core, filters JSON in-process using a generic `filter_response()` helper, returns subset. Repeatable query params = OR within field, different params = AND between fields.

**Tech Stack:** FastAPI, Pydantic, httpx

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `app/api/filter.py` (new) | Generic `filter_response()` helper |
| Modify | `app/api/v1/note.py` | Accept filter query params on `GET /notes/` |
| Modify | `app/api/v1/point.py` | Accept filter query params on `GET /points/` |
| Modify | `app/api/v1/author.py` | Accept filter query params on `GET /authors/` |

---

### Task 1: Create filter_response helper

**Files:**

- Create: `app/api/filter.py`

- [ ] **Step 1: Write `filter_response` function**

```python
from __future__ import annotations

from typing import Any


def filter_response(
    items: list[dict[str, Any]],
    filters: dict[str, list[int]],
    list_fields: set[str],
) -> list[dict[str, Any]]:
    """Filter a list of dicts by query parameters.

    Args:
        items: Raw JSON items from database-core.
        filters: Mapping of field name → list of accepted values.
                 Empty list means "no filter on this field".
        list_fields: Fields where the value is a list of dicts with an "id" key.
                     For these, the filter checks if any item.id matches.
                     For non-list fields, the filter checks direct equality.

    Logic:
        - Each field in filters is OR (any value matches).
        - Across fields is AND (all must match).
        - If no filters provided, returns items unchanged.
    """
    if not filters:
        return items

    result = []
    for item in items:
        match = True
        for field, values in filters.items():
            if not values:
                continue
            if field in list_fields:
                item_ids = [entry["id"] for entry in item.get(field, [])]
                if not any(v in item_ids for v in values):
                    match = False
                    break
            else:
                if item.get(field) not in values:
                    match = False
                    break
        if match:
            result.append(item)
    return result
```

- [ ] **Step 2: Commit**

```bash
git add app/api/filter.py
git commit -m "feat: add filter_response helper for gateway-side filtering"
```

---

### Task 2: Add filtering to GET /notes/

**Files:**

- Modify: `app/api/v1/note.py`

- [ ] **Step 1: Add query params and filtering to list endpoint**

Current `note.py` has no `list_notes` endpoint. The `/by-point/{point_id}` endpoint exists but the root `GET /notes/` is missing. Add it with filtering:

```python
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
```

- [ ] **Step 2: Verify app loads**

```bash
uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add app/api/v1/note.py
git commit -m "feat: add filtering to GET /notes/"
```

---

### Task 3: Add filtering to GET /points/

**Files:**

- Modify: `app/api/v1/point.py`

- [ ] **Step 1: Add query params and filtering to list_points**

```python
from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.cache import cached_proxy_get
from app.api.filter import filter_response
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
    return await cached_proxy_get(request.app.state.db_client, request.app.state.filter_cache, "points/filters")


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


@router.get("/", response_model=list[PointResponse])
async def list_points(
    request: Request,
    point_type_id: Optional[list[int]] = Query(default=None),
    point_subtype_id: Optional[list[int]] = Query(default=None),
    point_subsubtype_id: Optional[list[int]] = Query(default=None),
):
    """List points with optional filtering."""
    data = await proxy_get(
        request.app.state.db_client,
        "points/",
        params={"extended": "true"},
    )
    filters = {
        "point_type_id": point_type_id or [],
        "point_subtype_id": point_subtype_id or [],
        "point_subsubtype_id": point_subsubtype_id or [],
    }
    return filter_response(data, filters, list_fields=set())
```

- [ ] **Step 2: Verify app loads**

```bash
uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add app/api/v1/point.py
git commit -m "feat: add filtering to GET /points/"
```

---

### Task 4: Add filtering to GET /authors/

**Files:**

- Modify: `app/api/v1/author.py`

- [ ] **Step 1: Add query params and filtering to list_authors**

```python
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
```

- [ ] **Step 2: Verify app loads**

```bash
uv run python -c "from app.main import app; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add app/api/v1/author.py
git commit -m "feat: add filtering to GET /authors/"
```
