from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

security = HTTPBearer()

async def token_required(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        data = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return {"sub": data["sub"], "role": data["role"]}
    except JWTError:
        # ⚠️ Development fallback: always treat as student ID=3
        print("⚠️ JWT invalid or expired — using dummy student for dev")
        return {"sub": 3, "role": "student"}
