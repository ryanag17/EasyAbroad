from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.auth.models import User
from sqlalchemy.sql import text
from app.auth.hashing import Hasher
from app.admin.schemas import AdminCreateUser
from app.auth.token_service import create_access_token

async def fetch_all_users(db: AsyncSession, search=None, role=None, status=None):
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
        stmt = stmt.where(User.is_active == (status.lower() == "active"))

    if search:
        search = f"%{search.lower()}%"
        stmt = stmt.where(User.first_name.ilike(search))  # add last_name/email if needed

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


async def create_user_by_admin(user_data: AdminCreateUser, db: AsyncSession):
    # Create the new user object
    db_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=Hasher.get_password_hash(user_data.password),
        birthday=user_data.birthday,
        gender=user_data.gender,
        country_name=user_data.country_name,
        city=user_data.city,
        role=user_data.role,
        is_active=True
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # 🔐 Generate an access token for the newly created user
    access_token = create_access_token(data={"sub": str(db_user.id)})

    # ✅ Return the user details along with the token
    return {
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
        "access_token": access_token
    }