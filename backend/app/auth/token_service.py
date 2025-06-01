# backend/app/auth/token_service.py

import secrets
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.config import settings
from app.auth.models import RefreshToken


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token, embedding `data` (which must include 'sub' and 'role').
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = { **data, "exp": expire }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    """
    Create a new refresh token (a secure random string), store it in DB, and return it.
    """
    token   = secrets.token_urlsafe(32)
    now     = datetime.utcnow()
    expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(token=token, user_id=user_id, issued_at=now, expires_at=expires)
    db.add(db_token)
    await db.commit()
    return token


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    """
    Mark an existing refresh token as revoked (revoked=True).
    """
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.token == token)
        .values(revoked=True)
    )
    await db.commit()


async def rotate_refresh_token(db: AsyncSession, old_token: str, user_id: int) -> str:
    """
    Revoke the old refresh token, then issue and return a brand-new one.
    """
    await revoke_refresh_token(db, old_token)
    return await create_refresh_token(db, user_id)
