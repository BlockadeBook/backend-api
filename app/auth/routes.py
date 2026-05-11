from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.errors import UniqueViolation
from pydantic import BaseModel

from app.auth.decorators import admin_required
from app.config import get_jwt_secret
from app.db import get_cursor

auth_router = APIRouter(tags=["auth"])


class AuthRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/register", status_code=201)
async def register(body: AuthRequest, _admin=Depends(admin_required)):
    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    try:
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s) RETURNING id, username",
                (body.username, password_hash),
            )
            user = cur.fetchone()
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Username already exists")

    return {"id": user["id"], "username": user["username"]}


@auth_router.get("/me")
async def me(user=Depends(admin_required)):
    return {"id": user["id"], "username": user["username"]}


@auth_router.post("/login")
async def login(body: AuthRequest):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, username, password_hash FROM admin_users WHERE username = %s",
            (body.username,),
        )
        user = cur.fetchone()

    if not user or not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": user["id"],
        "username": user["username"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm="HS256")

    return {"token": token}
