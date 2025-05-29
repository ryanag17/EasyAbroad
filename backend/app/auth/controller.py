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
from app.auth.models import UserLogin, UserCreate, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.email_service import send_reset_email


async def register(
    db: AsyncSession,
    user: UserCreate
):
    # 1) Check for existing email
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2) Hash the password
    hashed_pw = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # 3) Create the User
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

    # 4) Seed Student or Consultant
    if new_user.role == "student":
        stud = Student(user_id=new_user.id)
        db.add(stud)
    elif new_user.role == "consultant":
        cons = Consultant(user_id=new_user.id)
        db.add(cons)
    await db.commit()

    # 5) Issue tokens
    access_token = create_access_token({"sub": new_user.id, "role": new_user.role})
    refresh_token = await create_refresh_token(db, new_user.id)

    return {"access_token": access_token, "refresh_token": refresh_token}


async def login(
    db: AsyncSession,
    creds: UserLogin
):
    # 1) Fetch user by email
    result = await db.execute(select(User).where(User.email == creds.email))
    user = result.scalars().first()
    if not user or not bcrypt.checkpw(
        creds.password.encode("utf-8"),
        user.hashed_password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2) Issue access token
    access_token = create_access_token({"sub": user.id, "role": user.role})
    # 3) Issue refresh token
    refresh_token = await create_refresh_token(db, user.id)

    return {"access_token": access_token, "refresh_token": refresh_token}


async def forgot_password(
    db: AsyncSession,
    data: ForgotPasswordRequest
):
    token = secrets.token_hex(16)
    expiry = datetime.utcnow() + timedelta(hours=1)
    await db.execute(
        text("UPDATE users SET reset_token = :token, token_expiry = :expiry WHERE email = :email"),
        {"token": token, "expiry": expiry, "email": data.email}
    )
    await db.commit()
    send_reset_email(data.email, token)
    return {"message": "Reset email sent if the address exists."}


async def reset_password(
    db: AsyncSession,
    data: ResetPasswordRequest
):
    # Validate token + expiry
    result = await db.execute(
        text("SELECT id, token_expiry FROM users WHERE reset_token = :token"),
        {"token": data.token}
    )
    row = result.first()
    if not row or row.token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await db.execute(
        text(
            "UPDATE users SET password_hash = :pw, reset_token = NULL, token_expiry = NULL WHERE id = :uid"
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
            "SELECT u.first_name, u.last_name, u.email, u.city, u.country,"
            " s.birthday, s.gender, s.languages, s.profile_picture"
            " FROM users u LEFT JOIN students s ON u.id = s.user_id"
            " WHERE u.id = :uid"
        ), {"uid": user_id}
    )
    profile = result.mappings().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return dict(profile)

async def update_student_profile(
    db: AsyncSession,
    user_id: int,
    data: dict
):
    # Update users table
    fields = {k: v for k, v in data.items() if k in ("first_name","last_name","email","city","country")}
    if fields:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**fields)
        )
        await db.execute(stmt)

    # Ensure students row exists
    await db.execute(
        text("INSERT IGNORE INTO students (user_id) VALUES (:uid)"),
        {"uid": user_id}
    )
    # Update students-specific
    stud_fields = {k: v for k, v in data.items() if k in ("birthday","gender","languages","profile_picture")}
    if stud_fields:
        await db.execute(
            update(Student)
            .where(Student.user_id == user_id)
            .values(**stud_fields)
        )
    await db.commit()
    return True