from datetime import datetime, timedelta
import bcrypt, secrets

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.auth.models import (
    User,
    UserCreate,
    UserLogin,
    Language,
    UserLanguage,
    RefreshToken,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.auth.token_service import create_access_token, create_refresh_token
from app.auth.email_service import send_reset_email


async def register(db: AsyncSession, user_in: UserCreate):
    # 1) Make sure nobody already signed up with that email
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2) Hash the plain-text password
    hashed_pw = bcrypt.hashpw(user_in.password.encode(), bcrypt.gensalt()).decode()

    # 3) Create the new User row: note field names must match the ORM (country_name, not country)
    new_user = User(
        first_name      = user_in.first_name,
        last_name       = user_in.last_name,
        email           = user_in.email,
        password_hash   = hashed_pw,
        role            = user_in.role.lower(),
        city            = user_in.city,
        country_name    = user_in.country_name,       # <— now always non-NULL
        birthday        = user_in.birthday,
        gender          = user_in.gender,
        profile_picture = user_in.profile_picture,
        access_level    = (user_in.access_level if user_in.role.lower() == "admin" else None)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 4) If any languages were provided, insert into user_languages join table
    if user_in.languages:
        for lang_id in user_in.languages:
            assoc = UserLanguage(user_id=new_user.id, language_id=lang_id)
            db.add(assoc)
        await db.commit()

    # 5) Issue JWT access + refresh tokens
    access_token  = create_access_token({"sub": str(new_user.id), "role": new_user.role})
    refresh_token = await create_refresh_token(db, new_user.id)

    return {
        "access_token" : access_token,
        "refresh_token": refresh_token,
        "role"         : new_user.role,
    }


async def login(db: AsyncSession, creds: UserLogin):
    # 1) Look up the user by e-mail
    result = await db.execute(select(User).where(User.email == creds.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2) Check bcrypt-hash
    if not bcrypt.checkpw(creds.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3) Issue new tokens
    access_token  = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = await create_refresh_token(db, user.id)
    return {
        "access_token" : access_token,
        "refresh_token": refresh_token,
        "role"         : user.role,
    }


async def forgot_password(db: AsyncSession, data: ForgotPasswordRequest):
    # Generate a one-time token for password reset
    token  = secrets.token_hex(16)
    expiry = datetime.utcnow() + timedelta(hours=1)

    # Save it into the users table (raw text).  We now have reset_token + token_expiry columns.
    await db.execute(
        text("UPDATE users SET reset_token=:t, token_expiry=:e WHERE email=:em"),
        {"t": token, "e": expiry, "em": data.email}
    )
    await db.commit()

    # Send the reset link by email
    send_reset_email(data.email, token)
    return {"message": "Reset email sent if the address exists."}


async def reset_password(db: AsyncSession, data: ResetPasswordRequest):
    # Find the user by reset_token
    result = await db.execute(
        text("SELECT id, token_expiry FROM users WHERE reset_token=:t"),
        {"t": data.token}
    )
    row = result.first()
    if not row or row.token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

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


async def get_student_profile(db: AsyncSession, user_id: int):
    # Only return if role == student
    stmt = select(
        User.first_name, User.last_name, User.email,
        User.city, User.country_name, User.birthday, User.gender,
        User.profile_picture
    ).where(User.id == user_id, User.role == "student")
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Fetch that user’s language names
    lang_stmt = (
        select(Language.language_name)
        .join(UserLanguage, UserLanguage.language_id == Language.id)
        .where(UserLanguage.user_id == user_id)
    )
    lang_result = await db.execute(lang_stmt)
    languages = list(lang_result.scalars().all())


    return {
        "first_name"      : row.first_name,
        "last_name"       : row.last_name,
        "email"           : row.email,
        "city"            : row.city,
        "country"         : row.country_name,
        "birthday"        : row.birthday,
        "gender"          : row.gender,
        "profile_picture" : row.profile_picture,
        "languages"       : languages
    }


async def get_consultant_profile(db: AsyncSession, user_id: int):
    stmt = select(
        User.first_name, User.last_name, User.email,
        User.city, User.country_name, User.birthday, User.gender,
        User.profile_picture
    ).where(User.id == user_id, User.role == "consultant")
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    lang_stmt = (
        select(Language.language_name)
        .join(UserLanguage, UserLanguage.language_id == Language.id)
        .where(UserLanguage.user_id == user_id)
    )
    lang_result = await db.execute(lang_stmt)
    languages = [r for r in lang_result.scalars().all()]


    return {
        "first_name"      : row.first_name,
        "last_name"       : row.last_name,
        "email"           : row.email,
        "city"            : row.city,
        "country"         : row.country_name,
        "birthday"        : row.birthday,
        "gender"          : row.gender,
        "profile_picture" : row.profile_picture,
        "languages"       : languages
    }
