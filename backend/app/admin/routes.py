from fastapi import APIRouter, Depends, status, HTTPException, Query, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.admin.controller import fetch_all_users, create_user_by_admin
from app.admin.schemas import UserOut, AdminCreateUser
from app.auth.models import User

router = APIRouter(
    prefix="/admin",
    tags=["admin-user-management"]
)

# ✅ Admin check
def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user  # return the user dict if needed in the route

# ✅ Secure route
@router.get("/users", response_model=list[UserOut])
async def get_all_users(
    search: str = Query(None),
    role: str = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),  # 👈 this enforces admin role
):
    return await fetch_all_users(db, search=search, role=role, status=status)

@router.post("/users", status_code=201)
async def admin_create_user(
    user_data: AdminCreateUser = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return await create_user_by_admin(user_data, db)



@router.get("/users/{user_id}")
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

    user.is_active = not user.is_active  # Flip the current value
    await db.commit()
    await db.refresh(user)

    return {
        "status": "success",
        "user_id": user.id,
        "new_status": "active" if user.is_active else "inactive"
    }