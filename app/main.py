from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.api import api_router
from app.config import config
from app.db.client import Client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_client = Client(config.database_api)
    yield
    await app.state.db_client.close()


app = FastAPI(title="backend", lifespan=lifespan)

app.include_router(api_router, prefix="/api")


# By default, return these responses for such errors.
# But you can always try&except them if you need different behaviour.

@app.exception_handler(httpx.RequestError)
async def httpx_request_error_handler(request: Request, e: httpx.RequestError):
    return await http_exception_handler(request, HTTPException(503))


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(request: Request, e: httpx.HTTPStatusError):
    return await http_exception_handler(request, HTTPException(e.response.status_code))
