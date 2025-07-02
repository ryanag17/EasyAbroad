import os, base64
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
from pydantic import BaseModel

from app.db import get_db
from app.auth.models import User
from app.messages.models import Message
from app.auth.token_verification import get_current_user
from app.messages.schemas import MessageOut
from app.messages.schemas import SendMessageSchema, MessageOut
from app.notification.models import Notification



fernet = Fernet(os.environ["MESSAGE_ENCRYPTION_KEY"].encode())
router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", response_model=dict, summary="Send message (with notification)")
async def send_message(
    data: SendMessageSchema,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if len(data.message) > 500:
        raise HTTPException(status_code=400, detail="Message cannot exceed 500 characters.")

    recipient = await db.get(User, data.receiver_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    token = fernet.encrypt(data.message.encode())
    raw = base64.urlsafe_b64decode(token)
    iv = raw[9:9 + 16]

    msg = Message(
        sender_id=user["user_id"],
        receiver_id=data.receiver_id,
        booking_id=data.booking_id,
        encrypted_message=token,
        encryption_iv=iv,
        sent_at=datetime.utcnow()
    )
    db.add(msg)

    sender_obj = await db.get(User, user["user_id"])
    sender_name = f"{sender_obj.first_name} {sender_obj.last_name}" if sender_obj else "A user"

    if recipient.role == "consultant":
        redirect_url = f"/consultant/chat.html?partnerId={user['user_id']}"
    elif recipient.role == "student":
        redirect_url = f"/student/chat.html?partnerId={user['user_id']}"
    else:
        if user["role"] == "consultant":
            redirect_url = "/consultant/messages.html"
        elif user["role"] == "student":
            redirect_url = "/student/messages.html"

    notif_content = f"You have received a new message from {sender_name}."
    new_notif = Notification(
        user_id=data.receiver_id,
        content=notif_content,
        type="info",
        redirect_url=redirect_url
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(msg)
    await db.refresh(new_notif)

    return {"status": "sent"}

@router.get("", response_model=List[MessageOut], summary="Fetches a list of last messages")
async def get_conversation_summaries(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  # changed
):
    q = await db.execute(
        select(Message)
        .where(
            or_(
                Message.sender_id == user["user_id"],
                Message.receiver_id == user["user_id"]
            )
        )
        .order_by(Message.sent_at.desc())
    )
    msgs = q.scalars().all()

    seen = set()
    out = []

    for m in msgs:
        partner_id = m.receiver_id if m.sender_id == user["user_id"] else m.sender_id
        if partner_id in seen:
            continue
        partner = await db.get(User, partner_id)
       
        seen.add(partner_id)
        text = fernet.decrypt(m.encrypted_message).decode()
        out.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": text,
            "from_me": (m.sender_id == user["user_id"]),
            "sent_at": m.sent_at,
            "first_name": partner.first_name,
            "last_name": partner.last_name,
        })

    return out


@router.get("/with/{partner_id}", response_model=List[MessageOut], summary="Chat summary")
async def get_full_thread(
    partner_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  # changed
):
    partner = await db.get(User, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="User not found")
 

    q = await db.execute(
        select(Message)
        .where(
            or_(
                (Message.sender_id == user["user_id"]) & (Message.receiver_id == partner_id),
                (Message.receiver_id == user["user_id"]) & (Message.sender_id == partner_id)
            )
        )
        .order_by(Message.sent_at.asc())
    )
    msgs = q.scalars().all()

    thread = []
    for m in msgs:
        text = fernet.decrypt(m.encrypted_message).decode()
        thread.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": text,
            "from_me": (m.sender_id == user["user_id"]),
            "sent_at": m.sent_at,
            "first_name": partner.first_name,
            "last_name": partner.last_name,
        })

    return thread

users_router = APIRouter(prefix="/users", tags=["users"])
@users_router.get("/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user_obj = result.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user_obj.id,
        "full_name": f"{user_obj.first_name} {user_obj.last_name}",
        "first_name": user_obj.first_name,
        "last_name": user_obj.last_name,
        "profile_picture": user_obj.profile_picture
    }



@router.delete("/with/{partner_id}")
async def delete_conversation(partner_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        Message.__table__.delete().where(
            or_(
                ((Message.sender_id == user["user_id"]) & (Message.receiver_id == partner_id)),
                ((Message.receiver_id == user["user_id"]) & (Message.sender_id == partner_id))
            )
        )
    )
    await db.commit()
    print("Deleted rows:", result.rowcount)  # Optional: for debugging
    return {"detail": "Conversation deleted"}