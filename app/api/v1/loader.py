from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.auth import admin_required

router = APIRouter(prefix="/loader", tags=["loader"])

POST_URLS = {"authors": "authors", "notes": "notes", "points": "points", "tags": "notes/tags"}


@router.post("/load", dependencies=[Depends(admin_required)])
async def load_data(request: Request):
    """Load JSON data (authors, notes, points, tags) into database-core.

    Accepts a JSON body with keys matching POST_URLS, each containing a list
    of objects to POST to the corresponding database-core endpoint.

    Example body:
    {
        "authors": [{"last_name": "Ivanov", "first_name": "Ivan", ...}],
        "notes": [{"author_id": 1, "citation": "...", ...}]
    }
    """
    body = await request.json()
    if not isinstance(body, dict):
        return JSONResponse(
            content={"error": "request body must be a JSON object"},
            status_code=400,
        )

    client = request.app.state.db_client
    results: dict[str, dict[str, Any]] = {}
    total_success = 0
    total_failed = 0

    for key, items in body.items():
        if key not in POST_URLS:
            results[key] = {"status": "skipped", "reason": f"unknown key '{key}'"}
            continue
        if not isinstance(items, list):
            results[key] = {"status": "skipped", "reason": "value must be a list"}
            continue

        success = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        for item in items:
            full_url = f"{client.base_url}/{POST_URLS[key]}"
            try:
                response = await client.post(full_url, json=item, timeout=10)
                response.raise_for_status()
                success += 1
            except Exception as exc:
                failed += 1
                errors.append({"item": item, "error": str(exc)})

        results[key] = {"posted": success, "failed": failed, "errors": errors}
        total_success += success
        total_failed += failed

    return JSONResponse(
        content={
            "total_posted": total_success,
            "total_failed": total_failed,
            "details": results,
        },
        status_code=200 if total_failed == 0 else 207,
    )
