import os, base64
from datetime import datetime
from typing import List, Optional
from hashids import Hashids
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet

from app.db import get_db
from app.auth.models import User
from app.messages.models import Message
from app.auth.token_verification import get_current_user
from app.messages.schemas import SendMessageSchema, MessageOut
from app.notification.models import Notification

# ─── Hashids setup ────────────────────────────────────────────────────────────
HASHIDS_SALT = os.getenv("HASHIDS_SALT", "change-me-please")
hashids = Hashids(salt=HASHIDS_SALT, min_length=8)

fernet = Fernet(os.environ["MESSAGE_ENCRYPTION_KEY"].encode())
router = APIRouter(prefix="/messages", tags=["messages"])


# ─── Send message with notification ────────────────────────────────────────────
@router.post("/send", response_model=dict, summary="Send message (with notification)")
async def send_message(
    data: SendMessageSchema,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if len(data.message) > 500:
        raise HTTPException(400, "Message cannot exceed 500 characters.")

    recipient = await db.get(User, data.receiver_id)
    if not recipient:
        raise HTTPException(404, "Recipient not found")
    if recipient.id == user["user_id"]:
        raise HTTPException(400, "You cannot send messages to yourself.")

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

    me_hash = hashids.encode(user["user_id"])
    if recipient.role == "consultant":
        redirect_url = f"/consultant/chat.html?partnerId={me_hash}"
    elif recipient.role == "student":
        redirect_url = f"/student/chat.html?partnerId={me_hash}"
    else:
        redirect_url = (
            "/consultant/messages.html"
            if user["role"] == "consultant"
            else "/student/messages.html"
        )

    sender_obj = await db.get(User, user["user_id"])
    sender_name = (
        f"{sender_obj.first_name} {sender_obj.last_name}"
        if sender_obj
        else "A user"
    )
    new_notif = Notification(
        user_id=data.receiver_id,
        content=f"You have received a new message from {sender_name}.",
        type="info",
        redirect_url=redirect_url
    )
    db.add(new_notif)

    await db.commit()
    return {"status": "sent"}


# ─── List recent conversations (summaries) ────────────────────────────────────
@router.get("", response_model=List[MessageOut], summary="Fetches a list of last messages")
async def get_conversation_summaries(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
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
        seen.add(partner_id)
        partner = await db.get(User, partner_id)
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
            "partner_hash": hashids.encode(partner_id)
        })
    return out


# ─── Fetch a full chat thread by HASH ─────────────────────────────────────────
@router.get("/with/{partner_hash}", response_model=List[MessageOut], summary="Chat summary")
async def get_full_thread(
    partner_hash: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    decoded = hashids.decode(partner_hash)
    if not decoded:
        raise HTTPException(404, "User not found")
    partner_id = decoded[0]

    partner = await db.get(User, partner_id)
    if not partner:
        raise HTTPException(404, "User not found")

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
            "partner_hash": partner_hash   # ← newly added so your schema validates
        })
    return thread


# ─── Delete conversation by HASH ─────────────────────────────────────────────
@router.delete("/with/{partner_hash}")
async def delete_conversation(
    partner_hash: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    decoded = hashids.decode(partner_hash)
    if not decoded:
        raise HTTPException(404, "User not found")
    partner_id = decoded[0]

    await db.execute(
        Message.__table__
        .delete()
        .where(
            or_(
                (Message.sender_id == user["user_id"]) & (Message.receiver_id == partner_id),
                (Message.receiver_id == user["user_id"]) & (Message.sender_id == partner_id)
            )
        )
    )
    await db.commit()
    return {"detail": "Conversation deleted"}


# ─── User lookup ──────────────────────────────────────────────────────────────
users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(404, "User not found")
    return {
        "id": u.id,
        "full_name": f"{u.first_name} {u.last_name}",
        "first_name": u.first_name,
        "last_name": u.last_name,
        "profile_picture": u.profile_picture
    }

@users_router.get("/by-hash/{partner_hash}")
async def get_user_by_hash(
    partner_hash: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    decoded = hashids.decode(partner_hash)
    if not decoded:
        raise HTTPException(404, "User not found")
    partner_id = decoded[0]
    result = await db.execute(select(User).where(User.id == partner_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(404, "User not found")
    return {
        "id": u.id,
        "full_name": f"{u.first_name} {u.last_name}",
        "first_name": u.first_name,
        "last_name": u.last_name,
        "profile_picture": u.profile_picture
    }
