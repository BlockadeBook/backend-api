from __future__ import annotations

from typing import Any

import httpx
from fastapi.responses import JSONResponse


async def proxy_get(
    client: httpx.AsyncClient,
    url_path: str,
    params: dict[str, Any] | None = None,
) -> JSONResponse:
    """Proxy a GET request to database-core and return the response."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.get(full_url, params=params, timeout=10)
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=200)
    except httpx.RequestError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=503)
    except httpx.HTTPStatusError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=exc.response.status_code)


async def proxy_post(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
    success_status: int = 201,
) -> JSONResponse:
    """Proxy a POST request to database-core and return the response."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.post(full_url, json=body, timeout=10)
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=success_status)
    except httpx.RequestError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=503)
    except httpx.HTTPStatusError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=exc.response.status_code)
