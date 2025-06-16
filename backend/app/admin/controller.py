from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.auth.models import User
from sqlalchemy.sql import text

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
