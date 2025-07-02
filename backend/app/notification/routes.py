from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import get_db
from app.notification import models as notif_models, schemas as notif_schemas
from app.auth.token_verification import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Student/Consultant/Admin: Get all notifications
@router.get("/me", response_model=List[notif_schemas.NotificationOut], summary="Student/Consultant/Admin: Get all notifications")
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stmt = select(notif_models.Notification).where(notif_models.Notification.user_id == current_user["user_id"]).order_by(notif_models.Notification.created_at.desc())
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    return notifications

# System: Create a notification manually
@router.post("/", response_model=notif_schemas.NotificationOut, summary="System: Create a notification manually")
async def create_notification(
    notif: notif_schemas.NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    new_notif = notif_models.Notification(**notif.dict())
    db.add(new_notif)
    await db.commit()
    await db.refresh(new_notif)
    return new_notif

# Student/Consultant/Admin: Mark a notification as read
@router.patch("/{notif_id}/mark-read", response_model=notif_schemas.NotificationOut, summary="Student/Consultant/Admin: Mark a notification as read")
async def mark_notification_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notif = await db.get(notif_models.Notification, notif_id)
    if not notif or notif.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif

# Student/Consultant/Admin: Mark a notification as unread
@router.patch("/{notif_id}/mark-unread", response_model=notif_schemas.NotificationOut, summary="Student/Consultant/Admin: Mark a notification as unread")
async def mark_notification_unread(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notif = await db.get(notif_models.Notification, notif_id)
    if not notif or notif.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
    notif.is_read = False
    await db.commit()
    await db.refresh(notif)
    return notif

# Student/Consultant/Admin: Delete a notification
@router.delete("/{notif_id}", response_model=dict, summary="Student/Consultant/Admin: Delete a notification")
async def delete_notification(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notif = await db.get(notif_models.Notification, notif_id)
    if not notif or notif.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
    await db.delete(notif)
    await db.commit()
    return {"detail": "Notification deleted successfully"}