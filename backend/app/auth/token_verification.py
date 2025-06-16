# app/auth/token_verification.py

from fastapi import HTTPException, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.auth.models import RefreshToken, User

security = HTTPBearer()  # for reading "Authorization: Bearer <token>" header

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),            # ← inject a DB session
) -> User:
    """
    Verify an access JWT from the Authorization header and return the full User instance.
    """
    raw_token = creds.credentials
    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    # load the User record
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user  # ← now downstream handlers get a User, not a dict


async def get_current_user_from_refresh(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a refresh token from an HttpOnly cookie, check the DB, and return
    {user_id, token, role}.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
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

    if (
        row is None
        or row.revoked
        or row.expires_at is None
        or row.expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return {"user_id": row.user_id, "token": row.token, "role": row.role}
