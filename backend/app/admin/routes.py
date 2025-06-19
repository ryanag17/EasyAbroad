from fastapi import APIRouter, Depends, status, HTTPException, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.admin.controller import fetch_all_users, create_user_by_admin
from app.admin.schemas import UserOut, AdminCreateUser
from app.auth.models import User


# FastAPI router for all admin endpoints.
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# Dependency ensuring that current user is an admin:
def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user 


# Retrieve users with optional filters.
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


# Allows admin to create new user account - sends JSON data in request & passes data to create_user_by_admin
@router.post("/users", status_code=201, summary="Admin: Create new user account")
async def admin_create_user(
    user_data: AdminCreateUser = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return await create_user_by_admin(user_data, db)


# Fetch a specific user by user_id -> returns detailed user info.
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
        "status": "active" if user.is_active else "inactive",
        "registered": user.created_at.strftime("%Y-%m-%d") if user.created_at else "-",
        "profile_picture": user.profile_picture or ""
    }


# Toggles is_active status of user -> deactivate/activate function under view-user.html.
@router.patch("/users/{user_id}/status", status_code=200, summary="Admin: Toggle user is_active status (deactivate/activate account)")
async def update_user_status(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active  # Flip the current value
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "user_id": user.id,
        "new_status": "active" if user.is_active else "inactive"
    }


# Deletes user from database -> delete account function under view-user.html.
@router.delete("/users/{user_id}", status_code=204, summary="Admin: Delete user account by ID")
async def delete_user_by_admin(
    user_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
