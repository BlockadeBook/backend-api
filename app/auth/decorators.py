import jwt
from fastapi import Header, HTTPException

from app.config import get_jwt_secret
from app.db import get_cursor


async def admin_required(authorization: str = Header(...)):
    """FastAPI dependency that validates a Bearer JWT and returns the admin user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = authorization[7:]
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    with get_cursor() as cur:
        cur.execute(
            "SELECT id, username FROM admin_users WHERE id = %s",
            (payload["sub"],),
        )
        user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
