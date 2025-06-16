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
    """
    1) Create a new User (with all merged fields).
    2) Hash password, store languages if provided.
    3) Issue access & refresh tokens.
    4) Return the access token in JSON and set the refresh token as an HttpOnly cookie.
    """
    result = await register(db, user)

    # Set HttpOnly cookie for refresh token:
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
    """
    1) Verify credentials, fetch user, compare bcrypt hash.
    2) Issue new access & refresh tokens.
    3) Return access token in JSON and set refresh token cookie.
    """
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
    """
    1) Read the refresh token from the HttpOnly cookie and verify it in the DB.
    2) Rotate: revoke the old refresh token, insert a new one.
    3) Issue a fresh access token (JWT) using the fetched role.
    4) Set the new refresh token cookie, return the new access token in JSON.
    """
    user_id   = user_data["user_id"]
    old_token = user_data["token"]
    role      = user_data["role"]

    # Rotate the refresh token in the DB (invalidate old, insert new):
    new_refresh = await rotate_refresh_token(db, old_token, user_id)

    # Create new access token using role:
    access_token = create_access_token({"sub": user_id, "role": role})

    # Overwrite the HttpOnly cookie with the new refresh token:
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,  # In production, set to True
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
    """
    1) Revoke the provided refresh token (from cookie) in the DB.
    2) Clear the refresh_token cookie.
    """
    await revoke_refresh_token(db, user_data["token"])
    response.delete_cookie(key="refresh_token", path="/")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    1) Generate a reset token, save it in users.reset_token & token_expiry.
    2) Send an email with a password-reset link.
    """
    return await forgot_password(db, data)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    1) Verify the reset token is valid & not expired.
    2) Hash the new password, update the user record, clear reset_token fields.
    """
    return await reset_password(db, data)


@router.get("/students/profile", status_code=status.HTTP_200_OK)
async def student_profile(
    user=Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    """
    Only a user with role="student" can reach here. Returns that student’s merged profile.
    """
    return await get_student_profile(db, user["user_id"])


@router.get("/consultants/profile", status_code=status.HTTP_200_OK)
async def consultant_profile(
    user=Depends(require_role("consultant")),
    db: AsyncSession = Depends(get_db),
):
    """
    Only a user with role="consultant" can reach here. Returns that consultant’s merged profile.
    """
    return await get_consultant_profile(db, user["user_id"])


@router.get("/debug-headers", status_code=status.HTTP_200_OK)
async def debug_headers(request: Request):
    """
    Returns a dict of all request headers—useful for debugging CORS or cookie issues.
    """
    return {k: v for k, v in request.headers.items()}

async def require_admin_user(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user