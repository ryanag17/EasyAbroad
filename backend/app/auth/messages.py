import os
import base64
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
from pydantic import BaseModel

from app.db import get_db
from app.auth.models import User, Message
from app.auth.token_verification import get_current_user


class SendMessageSchema(BaseModel):
    receiver_id: int
    message: str
    booking_id: Optional[int] = None

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    from_me: bool
    sent_at: datetime
    first_name: str
    last_name: str


fernet = Fernet(os.environ["MESSAGE_ENCRYPTION_KEY"].encode())
router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", response_model=dict)
async def send_message(
    data: SendMessageSchema,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  # changed
):
    recipient = await db.get(User, data.receiver_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if recipient.role == user["role"]:  # changed
        raise HTTPException(
            status_code=403,
            detail="Messaging is only allowed between students and consultants"
        )

    token = fernet.encrypt(data.message.encode())
    raw = base64.urlsafe_b64decode(token)
    iv = raw[9:9 + 16]

    msg = Message(
        sender_id=user["user_id"],  # changed
        receiver_id=data.receiver_id,
        booking_id=data.booking_id,
        encrypted_message=token,
        encryption_iv=iv,
        sent_at=datetime.utcnow()
    )
    db.add(msg)
    await db.commit()

    return {"status": "sent"}


@router.get("", response_model=List[MessageOut])
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
        if partner.role == user["role"]:  # changed
            continue

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


@router.get("/with/{partner_id}", response_model=List[MessageOut])
async def get_full_thread(
    partner_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)  # changed
):
    partner = await db.get(User, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="User not found")
    if partner.role == user["role"]:  # changed
        raise HTTPException(
            status_code=403,
            detail="Messaging is only allowed between students and consultants"
        )

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
