from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, text
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.admin.controller import fetch_all_users, create_user_by_admin
from app.admin.schemas import UserOut, AdminCreateUser
from app.auth.models import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user

@router.get("/users", response_model=list[UserOut], summary="Admin: Get all users with optional filters")
async def get_all_users(
    search: str = Query(None),
    column: str = Query("first_name"),
    role: str = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return await fetch_all_users(db, search=search, role=role, status=status, column=column)

@router.post("/users", status_code=201, summary="Admin: Create new user account")
async def admin_create_user(
    user_data: AdminCreateUser = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return await create_user_by_admin(user_data, db)

@router.get("/users/{user_id}", summary="Admin: Get full user info by ID")
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "birthday": str(user.birthday),
        "gender": user.gender,
        "country": user.country_name,
        "city": user.city,
        "status": user.is_active,  # 'active', 'inactive', or 'deleted'
        "registered": user.created_at.strftime("%Y-%m-%d") if user.created_at else "-",
        "profile_picture": user.profile_picture or ""
    }

@router.patch("/users/{user_id}/status", status_code=200)
async def update_user_status(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active == "deleted":
        raise HTTPException(status_code=400, detail="Cannot change status of a deleted account.")

    user.is_active = "inactive" if user.is_active == "active" else "active"
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "user_id": user.id,
        "new_status": user.is_active
    }

@router.delete("/users/{user_id}", status_code=204)
async def delete_user_by_admin(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active == "deleted":
        raise HTTPException(status_code=400, detail="User already deleted.")

    user.is_active = "deleted"

    # Manually delete linked data (these must match your schema)
    await db.execute(text("DELETE FROM Education WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM Internship WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM consultant_availability WHERE consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM bookings WHERE student_id = :uid OR consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("""
        DELETE FROM support_tickets WHERE user_id = :uid;
        DELETE FROM support_ticket_messages WHERE sender_id = :uid;
    """), {"uid": user_id})
    await db.execute(text("DELETE FROM appointments WHERE student_id = :uid OR consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM consultant_reviews WHERE student_id = :uid OR consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM notifications WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM refresh_tokens WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM user_languages WHERE user_id = :uid"), {"uid": user_id})

    # Delete old messages only
    await db.execute(text("""
        DELETE FROM messages
        WHERE (sender_id = :uid OR receiver_id = :uid)
        AND sent_at < DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """), {"uid": user_id})

    await db.commit()
