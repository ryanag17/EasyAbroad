from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.config import settings
from app.auth.models import UserCreate, UserLogin, TokenOut
from app.auth.controller import (
    register,
    login,
    get_student_profile,
    get_consultant_profile,
)
from app.auth.token_service import (
    create_access_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.auth.token_verification import (
    get_current_user,
    get_current_user_from_refresh,
)

router = APIRouter(tags=["auth"])


@router.get("/me")
async def who_am_i(user=Depends(get_current_user)):
    """
    Debug endpoint: returns whatever FastAPI decoded from your Bearer JWT.
    """
    return user


def require_role(role_name: str):
    async def checker(user=Depends(get_current_user)):
        if user["role"] != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return checker


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register_endpoint(
    user: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await register(db, user)
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,            # ← set True in prod
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"access_token": result["access_token"], "token_type": "bearer"}


@router.post("/login", response_model=TokenOut)
async def login_endpoint(
    creds: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await login(db, creds)
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"access_token": result["access_token"], "token_type": "bearer"}


@router.post("/refresh", response_model=TokenOut)
async def refresh_token_endpoint(
    response: Response,
    user_data=Depends(get_current_user_from_refresh),
    db: AsyncSession = Depends(get_db),
):
    user_id   = user_data["user_id"]
    old_token = user_data["token_record"].token

    new_refresh = await rotate_refresh_token(db, old_token, user_id)
    access_token = create_access_token({
        "sub":  user_id,
        "role": user_data["token_record"].user.role
    })

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(
    response: Response,
    user_data=Depends(get_current_user_from_refresh),
    db: AsyncSession = Depends(get_db),
):
    await revoke_refresh_token(db, user_data["token_record"].token)
    response.delete_cookie(key="refresh_token", path="/")
    return


@router.get("/students/profile")
async def student_profile(
    user=Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    return await get_student_profile(db, user["user_id"])


@router.get("/consultants/profile")
async def consultant_profile(
    user=Depends(require_role("consultant")),
    db: AsyncSession = Depends(get_db),
):
    return await get_consultant_profile(db, user["user_id"])
