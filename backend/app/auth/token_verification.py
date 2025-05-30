
# backend/app/auth/token_verification.py

from fastapi import HTTPException, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.db import get_db
from app.auth.models import RefreshToken

security = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    raw_token = creds.credentials
    print("🛠️ Raw token:", raw_token)
    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        print("🛠️ Decoded payload:", payload)
        return {"user_id": payload["sub"], "role": payload.get("role")}
    except JWTError as e:
        print("❌ JWTError:", str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

async def get_current_user_from_refresh(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalars().first()

    if (
        db_token is None
        or db_token.revoked
        or db_token.expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    return {"user_id": db_token.user_id, "token_record": db_token}
