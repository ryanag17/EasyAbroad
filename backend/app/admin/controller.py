from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, select, or_
from app.auth.models import User
from sqlalchemy.sql import text
from datetime import datetime, timedelta
import secrets
import bcrypt
from sqlalchemy import text
from app.auth.models import User, UserLanguage
from app.auth.email_service import send_verification_email


# Fetches list of users from the users database table - filters users by different variables - search term based on column types.
async def fetch_all_users(db: AsyncSession, search=None, role=None, status=None, column="first_name"):
    stmt = select(
        User.id,
        User.first_name,
        User.last_name,
        User.email,
        User.role,
        User.is_active,
        User.created_at
    )

    if role:
        stmt = stmt.where(User.role == role)

    if status:
        stmt = stmt.where(User.is_active == status.lower())

    if search:
        search = f"%{search.lower()}%"
        column_map = {
            "first_name": User.first_name,
            "last_name": User.last_name,
            "email": User.email,
            "id": User.id.cast(String),
        }

        if column in column_map:
            stmt = stmt.where(column_map[column].ilike(search))
        else:
            stmt = stmt.where(User.first_name.ilike(search)) 

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": row.id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "role": row.role,
            "is_active": row.is_active,
            "created_at": row.created_at,
        }
        for row in rows
    ]



# Creates new user account in the database using data filled out by an admin - returns user info along with access token.
async def create_user_by_admin(user_in, db):
    # Check if email already exists
    result = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user_in.email})
    if result.first():
        raise Exception("Email already registered")

    # Hash password
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
        access_level=(user_in.access_level if user_in.role.lower() == "admin" else None),
        is_verified=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate verification token and expiry
    verification_token = secrets.token_hex(16)
    expiry = datetime.now() + timedelta(hours=24)

    await db.execute(
        text("UPDATE users SET verification_token=:t, verification_token_expiry=:e WHERE id=:uid"),
        {"t": verification_token, "e": expiry, "uid": new_user.id}
    )
    await db.commit()

    # Send email
    send_verification_email(new_user.email, verification_token, f"{new_user.first_name} {new_user.last_name}")

    # If languages included, add them
    if hasattr(user_in, "languages") and user_in.languages:
        for lang_id in user_in.languages:
            assoc = UserLanguage(user_id=new_user.id, language_id=lang_id)
            db.add(assoc)
        await db.commit()

    return {
        "status": "success",
        "user_id": new_user.id,
        "message": "User created and verification email sent."
    }