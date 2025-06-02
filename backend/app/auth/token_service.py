import secrets
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from fastapi import HTTPException
from app.config import settings
from app.auth.models import RefreshToken


def create_access_token(data: dict) -> str:
    # Ensure the required fields exist BEFORE encoding
    assert "sub" in data and "role" in data, "JWT payload missing 'sub' or 'role'"

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {**data, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    try:
        token = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        expires = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            issued_at=now,
            expires_at=expires
        )

        db.add(db_token)
        await db.commit()

        return token

    except Exception as e:
        print("❌ Failed to create refresh token:", e)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Refresh token error")


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
