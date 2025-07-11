from fastapi import APIRouter, Depends, Response, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from datetime import datetime, timedelta, timezone
import bcrypt, secrets
from app.db import get_db
from app.config import settings
from app.auth.email_service import send_reset_email, send_verification_email
import secrets
from app.auth.models import (
    User, UserLanguage, Language, Country, RefreshToken
)
from app.auth.schemas import (
    UserCreate, UserLogin, TokenOut, ForgotPasswordRequest, ResetPasswordRequest,
)
from app.profile.routes import (
    get_student_profile, get_consultant_profile,
)
from app.auth.token_service import (
    create_access_token, revoke_refresh_token, rotate_refresh_token
)
from app.auth.token_verification import (
    get_current_user, get_current_user_from_refresh
)
from app.auth.token_service import create_access_token, create_refresh_token
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/auth", tags=["auth"])

from app.auth.models import User


@router.get("/me", summary="Returns current logged users profile" )
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

async def register(db: AsyncSession, user_in: UserCreate):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hashpw(user_in.password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        password_hash=hashed_pw,
        role=user_in.role.lower(),
        city=user_in.city,
        country_name=user_in.country_name,
        birthday=user_in.birthday,
        gender=user_in.gender,
        profile_picture=user_in.profile_picture,
        access_level=(user_in.access_level if user_in.role.lower() == "admin" else None)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    verification_token = secrets.token_hex(16)
    expiry = datetime.now(timezone.utc) + timedelta(hours=24)

    await db.execute(
        text("UPDATE users SET verification_token=:t, verification_token_expiry=:e WHERE id=:uid"),
        {"t": verification_token, "e": expiry, "uid": new_user.id}
    )
    await db.commit()

    send_verification_email(new_user.email, verification_token, f"{new_user.first_name} {new_user.last_name}")

    if user_in.languages:
        for lang_id in user_in.languages:
            assoc = UserLanguage(user_id=new_user.id, language_id=lang_id)
            db.add(assoc)
        await db.commit()

    access_token = create_access_token({"sub": str(new_user.id), "role": new_user.role})
    refresh_token = await create_refresh_token(db, new_user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": new_user.role,
    }


async def login(db: AsyncSession, creds: UserLogin):
    result = await db.execute(select(User).where(User.email == creds.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_active == "deleted":
        raise HTTPException(
            status_code=403,
            detail="Your account has been deleted by an administrator and can no longer be accessed. Please contact support if you believe this is a mistake."
        )

    if user.is_active != "active":
        raise HTTPException(status_code=403, detail="Account is not active")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")

    if not bcrypt.checkpw(creds.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = await create_refresh_token(db, user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": user.role,
    }


@router.post(
    "/register", 
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED, 
    summary="Register function"
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
        secure=True,  # In production, switch this to True
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": result["access_token"],
        "token_type":   "bearer",
        "role":         result["role"],
    }

@router.get("/verify-email", summary="Verify email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT id, verification_token_expiry FROM users WHERE verification_token=:t"),
        {"t": token}
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    # Convert DB datetime to aware
    expiry = row.verification_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        await db.execute(
            text("DELETE FROM users WHERE id=:uid"),
            {"uid": row.id}
        )
        await db.commit()
        raise HTTPException(status_code=400, detail="Verification token expired")

    await db.execute(
        text(
            "UPDATE users "
            "SET is_verified=1, verification_token=NULL, verification_token_expiry=NULL "
            "WHERE id=:uid"
        ),
        {"uid": row.id}
    )
    await db.commit()

    return {"message": "Verification successful"}


@router.post("/login", response_model=TokenOut, summary="Log in")
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
        secure=True,  # In production, set to True
        samesite="strict",
        path="/",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )

    return {
        "access_token": result["access_token"],
        "token_type":   "bearer",
        "role":         result["role"],
    }


@router.post("/refresh", response_model=TokenOut, summary="Refresh token")
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


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log out")
async def logout_endpoint(
    response: Response,
    user_data=Depends(get_current_user_from_refresh),
    db: AsyncSession = Depends(get_db),
):
    await revoke_refresh_token(db, user_data["token"])
    response.delete_cookie(key="refresh_token", path="/")

@router.get("/students/profile", status_code=status.HTTP_200_OK, summary="Student full profile")
async def student_profile(
    user=Depends(require_role("student")),
    db: AsyncSession = Depends(get_db),
):
    return await get_student_profile(db, user["user_id"])


@router.get("/consultants/profile", status_code=status.HTTP_200_OK, summary="Consultant full profile")
async def consultant_profile(
    user=Depends(require_role("consultant")),
    db: AsyncSession = Depends(get_db),
):
    return await get_consultant_profile(db, user["user_id"])


@router.get("/debug-headers", status_code=status.HTTP_200_OK, summary="Required admin user")
async def debug_headers(request: Request):
    return {k: v for k, v in request.headers.items()}

async def require_admin_user(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an admin to access this resource"
        )
    return user



async def forgot_password(db: AsyncSession, data: ForgotPasswordRequest):
    # 1. Check if the email exists and user is active
    result = await db.execute(
        text("SELECT first_name, last_name, is_active FROM users WHERE email=:em"),
        {"em": data.email}
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Email not registered")

    if row.is_active != "active":
        raise HTTPException(status_code=403, detail="Account is not active or has been deleted. Password reset is not allowed.")

    # 2. Generate a one-time token for password reset
    token  = secrets.token_hex(16)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)

    # 3. Save it into the users table
    await db.execute(
        text("UPDATE users SET reset_token=:t, token_expiry=:e WHERE email=:em"),
        {"t": token, "e": expiry, "em": data.email}
    )
    await db.commit()

    user_name = f"{row.first_name} {row.last_name}"

    # 4. Send the reset link by email
    send_reset_email(data.email, token, user_name)
    return {"message": "Reset email sent if the address exists."}

async def reset_password(db: AsyncSession, data: ResetPasswordRequest):
    # Find the user by reset_token
    result = await db.execute(
        text("SELECT id, token_expiry, password_hash FROM users WHERE reset_token=:t"),
        {"t": data.token}
    )
    row = result.first()
    if not row or row.token_expiry < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # 1. Enforce password length
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")

    # 2. Prevent reusing the same password
    import bcrypt
    if bcrypt.checkpw(data.password.encode(), row.password_hash.encode()):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password.")

    # Hash the new password
    hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    await db.execute(
        text(
            "UPDATE users "
            "SET password_hash=:pw, reset_token=NULL, token_expiry=NULL "
            "WHERE id=:uid"
        ),
        {"pw": hashed_pw, "uid": row.id}
    )
    await db.commit()
    return {"message": "Password reset successfully"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK, summary="Forgot password - email sent with link")
async def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await forgot_password(db, data)


@router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Forgot password")
async def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await reset_password(db, data)

@router.get("/verify-reset-token", status_code=200, summary="Verify reset token validity")
async def verify_reset_token(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT token_expiry FROM users WHERE reset_token=:t"),
        {"t": token}
    )
    row = result.first()

    if not row or row.token_expiry < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return {"message": "Token is valid"}


async def delete_expired_unverified_users(db: AsyncSession):
    await db.execute(
        text("""
            DELETE FROM users
            WHERE is_verified = 0
              AND verification_token_expiry < :now
        """),
        {"now": datetime.now(timezone.utc)}
    )
    await db.commit()
    print("✅ Expired unverified users cleaned up.")
