from fastapi import APIRouter, Depends, Response, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.config import settings
from app.auth.models import (
    UserCreate,
    UserLogin,
    TokenOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.auth.controller import (
    register,
    login,
    get_student_profile,
    get_consultant_profile,
    forgot_password,
    reset_password
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

from app.auth.models import User


@router.get("/me")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {
        "id": current_user.id,
        "name": current_user.first_name,
        "surname": current_user.last_name,
        "email": current_user.email,
        "role": current_user.role,
        "city": current_user.city,
        "country_name": current_user.country_name,
    }


def require_role(role_name: str):
    async def checker(user=Depends(get_current_user)):
        if not user or user.get("role") != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return checker


@router.post(
    "/register",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED
)
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
        secure=False,  # In production, switch this to True
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": result["access_token"],
        "token_type":   "bearer",
        "role":         result["role"],
    }


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
        secure=False,  # In production, set to True
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": result["access_token"],
        "token_type":   "bearer",
        "role":         result["role"],
    }


@router.post("/refresh", response_model=TokenOut)
async def refresh_token_endpoint(
    response: Response,
    user_data=Depends(get_current_user_from_refresh),
    db: AsyncSession = Depends(get_db),
):
    user_id   = user_data["user_id"]
    old_token = user_data["token"]
    role      = user_data["role"]

    new_refresh = await rotate_refresh_token(db, old_token, user_id)
    access_token = create_access_token({"sub": user_id, "role": role})

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": access_token,
        "token_type":   "bearer",
        "role":         role,
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(
    response: Response,
    user_data=Depends(get_current_user_from_refresh),
    db: AsyncSession = Depends(get_db),
):
    await revoke_refresh_token(db, user_data["token"])
    response.delete_cookie(key="refresh_token", path="/")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await forgot_password(db, data)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await reset_password(db, data)


@router.get("/students/profile", status_code=status.HTTP_200_OK)
async def student_profile(
    user=Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    return await get_student_profile(db, user["user_id"])


@router.get("/consultants/profile", status_code=status.HTTP_200_OK)
async def consultant_profile(
    user=Depends(require_role("consultant")),
    db: AsyncSession = Depends(get_db),
):
    return await get_consultant_profile(db, user["user_id"])


@router.get("/debug-headers", status_code=status.HTTP_200_OK)
async def debug_headers(request: Request):
    return {k: v for k, v in request.headers.items()}

<<<<<<< HEAD
async def require_admin_user(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user
=======

# ─── Remove or comment out all legacy /messages handlers below ────────────
# from .models import Message, User
# from .schemas.message import SendMessageSchema, MessageOut
# from .token_verification import get_current_user
# from cryptography.fernet import Fernet
# import os
#
# router = APIRouter()
# fernet = Fernet(os.getenv("MESSAGE_ENCRYPTION_KEY").encode())
#
# @router.post("/messages/send", ...)
# async def send_message(...):
#     ...
#
# @router.get("/messages", ...)
# async def get_conversation_summaries(...):
#     ...
#
# @router.get("/messages/with/{partner_id}", ...)
# async def get_full_thread(...):
#     ...
# ────────────────────────────────────────────────────────────────────────────
>>>>>>> e1620af27e317f99bd710cf096af792cdf1b4eb9
