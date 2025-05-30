from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
from datetime import datetime, timedelta
import bcrypt
import secrets

from app.auth.token_service import (
    create_access_token,
    create_refresh_token
)
from app.auth.models import User, Student, Consultant
from app.auth.models import (
    UserLogin,
    UserCreate,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.auth.email_service import send_reset_email


async def register(
    db: AsyncSession,
    user: UserCreate
):
    # 1) Check email
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(400, "Email already registered")

    # 2) Hash pw
    hashed_pw = bcrypt.hashpw(
        user.password.encode(), bcrypt.gensalt()
    ).decode()

    # 3) Create user
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role.lower(),
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 4) Seed student or consultant
    if new_user.role == "student":
        db.add(Student(user_id=new_user.id))
    elif new_user.role == "consultant":
        db.add(Consultant(user_id=new_user.id))
    await db.commit()

    # 5) Issue tokens (cast 'sub' claim to string)
    access_token = create_access_token({
        "sub": str(new_user.id),
        "role": new_user.role
    })
    refresh_token = await create_refresh_token(db, new_user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


async def login(db: AsyncSession, creds: UserLogin):
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == creds.email))
    user = result.scalars().first()
    print(f"[DEBUG] login: lookup email={creds.email!r} → user={user!r}")

    # If no user, bail out
    if not user:
        print("[DEBUG] login: no user found, raising 401")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password
    print(f"[DEBUG] login: stored_hash={user.password_hash!r}")
    is_valid = bcrypt.checkpw(creds.password.encode(), user.password_hash.encode())
    print(f"[DEBUG] login: bcrypt.checkpw → {is_valid}")
    if not is_valid:
        print("[DEBUG] login: password mismatch, raising 401")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Issue tokens (cast 'sub' claim to string)
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })
    refresh_token = await create_refresh_token(db, user.id)
    print("[DEBUG] login: issuing tokens")
    return {"access_token": access_token, "refresh_token": refresh_token}


async def forgot_password(
    db: AsyncSession,
    data: ForgotPasswordRequest
):
    token = secrets.token_hex(16)
    expiry = datetime.utcnow() + timedelta(hours=1)
    await db.execute(
        text("UPDATE users SET reset_token=:t, token_expiry=:e WHERE email=:em"),
        {"t": token, "e": expiry, "em": data.email}
    )
    await db.commit()
    send_reset_email(data.email, token)
    return {"message": "Reset email sent if the address exists."}


async def reset_password(
    db: AsyncSession,
    data: ResetPasswordRequest
):
    result = await db.execute(
        text("SELECT id, token_expiry FROM users WHERE reset_token=:t"),
        {"t": data.token}
    )
    row = result.first()
    if not row or row.token_expiry < datetime.utcnow():
        raise HTTPException(400, "Invalid or expired token")

    hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()
    await db.execute(
        text(
            "UPDATE users SET password_hash=:pw, reset_token=NULL, token_expiry=NULL WHERE id=:uid"
        ),
        {"pw": hashed_pw, "uid": row.id}
    )
    await db.commit()
    return {"message": "Password reset successfully"}


async def get_student_profile(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        text(
            "SELECT u.first_name, u.last_name, u.email, u.city, u.country, "
            "s.birthday, s.gender, s.languages, s.profile_picture "
            "FROM users u LEFT JOIN students s ON u.id=s.user_id WHERE u.id=:uid"
        ), {"uid": user_id}
    )
    profile = result.mappings().first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return dict(profile)


async def get_consultant_profile(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        text(
            "SELECT u.first_name, u.last_name, u.email, u.city, u.country, "
            "c.birthday, c.gender, c.focus, c.languages, c.place_of_work "
            "FROM users u JOIN consultants c ON u.id=c.user_id WHERE u.id=:uid"
        ), {"uid": user_id}
    )
    profile = result.mappings().first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return dict(profile)
