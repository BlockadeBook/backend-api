from __future__ import annotations

import os
import time
from typing import Any

import httpx
from fastapi.responses import JSONResponse

DEFAULT_TTL = 300  # 5 minutes


async def cached_proxy_get(
    client: httpx.AsyncClient,
    cache: dict[str, dict[str, Any]],
    url_path: str,
    ttl: int = DEFAULT_TTL,
) -> JSONResponse:
    """Proxy a GET request with in-memory TTL caching.

    On cache hit, returns a stored JSONResponse without contacting database-core.
    On miss, proxies the request, stores the response, and returns it.
    """
    now = time.monotonic()
    entry = cache.get(url_path)
    if entry and now - entry["ts"] < ttl:
        return JSONResponse(content=entry["data"], status_code=200)

    full_url = f"{client.base_url}/{url_path}"
    try:
        response = await client.get(full_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except httpx.RequestError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=503)
    except httpx.HTTPStatusError as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=exc.response.status_code)

    ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", ttl))
    cache[url_path] = {"data": data, "ts": now}
    return JSONResponse(content=data, status_code=200)
