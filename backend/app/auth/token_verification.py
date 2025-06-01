# backend/app/auth/token_verification.py

from fastapi import HTTPException, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join

from app.config import settings
from app.db import get_db
from app.auth.models import RefreshToken, User

security = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verifies a bearer access token (JWT) and returns a dict with user_id and role.
    """
    raw_token = creds.credentials
    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return {"user_id": int(payload["sub"]), "role": payload.get("role")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


async def get_current_user_from_refresh(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies a refresh-token cookie, checks it in the database (not revoked/expired),
    and returns a dict with user_id, the raw token string, and the user's role.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        # Join RefreshToken -> User in a single query to fetch token record + user.role
        stmt = (
            select(
                RefreshToken.user_id,
                RefreshToken.token,
                RefreshToken.revoked,
                RefreshToken.expires_at,
                User.role
            )
            .join(User, RefreshToken.user_id == User.id)
            .where(RefreshToken.token == refresh_token)
        )
        result = await db.execute(stmt)
        row = result.first()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # If not found, revoked, or expired, reject
    if (
        row is None
        or row.revoked
        or row.expires_at is None
        or row.expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return {"user_id": row.user_id, "token": row.token, "role": row.role}
