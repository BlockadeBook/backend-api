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
    data, status = await fetch_get(client, url_path, params)
    return JSONResponse(content=data, status_code=status)


async def fetch_get(
    client: httpx.AsyncClient,
    url_path: str,
    params: dict[str, Any] | None = None,
) -> tuple[Any, int]:
    """Proxy a GET request and return (json_body, status_code)."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.get(full_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json(), 200
    except httpx.RequestError as exc:
        return {"error": str(exc)}, 503
    except httpx.HTTPStatusError as exc:
        return {"error": str(exc)}, exc.response.status_code


async def proxy_post(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
    success_status: int = 201,
) -> JSONResponse:
    """Proxy a POST request to database-core and return the response."""
    data, status = await fetch_post(client, url_path, body, success_status)
    return JSONResponse(content=data, status_code=status)


async def fetch_post(
    client: httpx.AsyncClient,
    url_path: str,
    body: dict | list,
    success_status: int = 201,
) -> tuple[Any, int]:
    """Proxy a POST request and return (json_body, status_code)."""
    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.post(full_url, json=body, timeout=10)
        response.raise_for_status()
        return response.json(), success_status
    except httpx.RequestError as exc:
        return {"error": str(exc)}, 503
    except httpx.HTTPStatusError as exc:
        return {"error": str(exc)}, exc.response.status_code