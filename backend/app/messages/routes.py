import os, base64
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.fernet import Fernet
from pydantic import BaseModel
import uuid

from app.db import get_db
from app.auth.models import User
from app.messages.models import Message
from app.auth.token_verification import get_current_user
from app.messages.schemas import SendMessageSchema, MessageOut
from app.notification.models import Notification
from app.messages.models import Conversation


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

    receiver_id = None

    # Determine receiver
    if data.conversation_id:
        # Find conversation
        q = await db.execute(
            select(Conversation).where(Conversation.public_id == data.conversation_id)
        )
        conversation = q.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Determine recipient
        if user["user_id"] == conversation.user_a_id:
            receiver_id = conversation.user_b_id
        elif user["user_id"] == conversation.user_b_id:
            receiver_id = conversation.user_a_id
        else:
            raise HTTPException(status_code=403, detail="You are not a participant of this conversation.")
    elif data.receiver_id:
        receiver_id = data.receiver_id
        # Find or create conversation
        q = await db.execute(
            select(Conversation).where(
                or_(
                    (Conversation.user_a_id == user["user_id"]) & (Conversation.user_b_id == receiver_id),
                    (Conversation.user_a_id == receiver_id) & (Conversation.user_b_id == user["user_id"])
                )
            )
        )
        conversation = q.scalar_one_or_none()
        if not conversation:
            conversation = Conversation(
                user_a_id=user["user_id"],
                user_b_id=receiver_id
            )
            db.add(conversation)
            await db.flush()  # Ensure conversation.id is generated
    else:
        raise HTTPException(status_code=400, detail="Either receiver_id or conversation_id must be provided.")

    if receiver_id == user["user_id"]:
        raise HTTPException(status_code=400, detail="You cannot send messages to yourself.")

    recipient = await db.get(User, receiver_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found.")

    # Encrypt
    token = fernet.encrypt(data.message.encode())
    raw = base64.urlsafe_b64decode(token)
    iv = raw[9:9 + 16]

    msg = Message(
        public_id=str(uuid.uuid4()),
        sender_id=user["user_id"],
        receiver_id=receiver_id,
        conversation_id=conversation.id,
        booking_id=data.booking_id,
        encrypted_message=token,
        encryption_iv=iv,
        sent_at=datetime.utcnow()
    )
    db.add(msg)

    # Notification
    sender_obj = await db.get(User, user["user_id"])
    sender_name = f"{sender_obj.first_name} {sender_obj.last_name}" if sender_obj else "A user"

    notif_content = f"You have received a new message from {sender_name}."

    if recipient.role == "consultant":
        redirect_url = f"/consultant/chat.html?conversationId={conversation.public_id}"
    elif recipient.role == "student":
        redirect_url = f"/student/chat.html?conversationId={conversation.public_id}"
    else:
        redirect_url = "/"

    new_notif = Notification(
        user_id=receiver_id,
        content=notif_content,
        type="info",
        redirect_url=redirect_url
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(msg)
    await db.refresh(new_notif)

    return {"status": "sent", "conversation_public_id": conversation.public_id}


@router.get("", response_model=List[MessageOut], summary="Fetches a list of last messages")
async def get_conversation_summaries(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    q = await db.execute(
        select(Message).where(
            or_(
                Message.sender_id == user["user_id"],
                Message.receiver_id == user["user_id"]
            )
        ).order_by(Message.sent_at.desc())
    )
    msgs = q.scalars().all()

    seen_conversations = set()
    out = []

    for m in msgs:
        if m.conversation_id in seen_conversations:
            continue

        hidden_ids = []
        if m.hidden_for_user_ids:
            hidden_ids = json.loads(m.hidden_for_user_ids)

        if user["user_id"] in hidden_ids:
            continue

        q2 = await db.execute(select(Conversation).where(Conversation.id == m.conversation_id))
        conversation = q2.scalars().first()
        if not conversation:
            continue

        partner_id = m.receiver_id if m.sender_id == user["user_id"] else m.sender_id
        partner = await db.get(User, partner_id)
        if not partner:
            continue

        seen_conversations.add(m.conversation_id)

        text = fernet.decrypt(m.encrypted_message).decode()
        out.append({
            "public_id": m.public_id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": text,
            "from_me": (m.sender_id == user["user_id"]),
            "sent_at": m.sent_at,
            "first_name": partner.first_name,
            "last_name": partner.last_name,
            "conversation_public_id": conversation.public_id,
        })

    return out


from fastapi import Path

@router.get("/with/{conversation_public_id}", response_model=List[MessageOut], summary="Chat summary")
async def get_full_thread(
    conversation_public_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    q = await db.execute(select(Conversation).where(Conversation.public_id == conversation_public_id))
    conversation = q.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Verify user is part of conversation
    if user["user_id"] not in [conversation.user_a_id, conversation.user_b_id]:
        raise HTTPException(status_code=403, detail="You are not part of this conversation")

    partner_id = conversation.user_a_id if conversation.user_b_id == user["user_id"] else conversation.user_b_id
    partner = await db.get(User, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    q = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sent_at.asc())
    )
    msgs = q.scalars().all()

    thread = []
    for m in msgs:
        hidden_ids = []
        if m.hidden_for_user_ids:
            hidden_ids = json.loads(m.hidden_for_user_ids)

        if user["user_id"] in hidden_ids:
            continue

        text = fernet.decrypt(m.encrypted_message).decode()
        thread.append({
            "public_id": m.public_id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": text,
            "from_me": (m.sender_id == user["user_id"]),
            "sent_at": m.sent_at,
            "first_name": partner.first_name,
            "last_name": partner.last_name,
            "conversation_public_id": conversation.public_id,
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



from sqlalchemy import update
import json

@router.delete("/with/{conversation_public_id}")
async def delete_conversation(conversation_public_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = await db.execute(select(Conversation).where(Conversation.public_id == conversation_public_id))
    conversation = q.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if user["user_id"] not in [conversation.user_a_id, conversation.user_b_id]:
        raise HTTPException(status_code=403, detail="You are not part of this conversation")

    # Fetch all messages in conversation
    q_msgs = await db.execute(select(Message).where(Message.conversation_id == conversation.id))
    msgs = q_msgs.scalars().all()

    for msg in msgs:
        hidden_ids = []
        if msg.hidden_for_user_ids:
            hidden_ids = json.loads(msg.hidden_for_user_ids)

        if user["user_id"] not in hidden_ids:
            hidden_ids.append(user["user_id"])

        stmt = (
            update(Message)
            .where(Message.id == msg.id)
            .values(hidden_for_user_ids=json.dumps(hidden_ids))
        )
        await db.execute(stmt)

    await db.commit()
    return {"detail": "Conversation hidden for current user"}

from pydantic import BaseModel

class StartConversationSchema(BaseModel):
    receiver_id: int

@router.post("/start-conversation", response_model=dict)
async def start_conversation(
    data: StartConversationSchema,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    receiver_id = data.receiver_id

    if receiver_id == user["user_id"]:
        raise HTTPException(status_code=400, detail="You cannot create a conversation with yourself.")

    recipient = await db.get(User, receiver_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Find or create conversation
    q = await db.execute(
        select(Conversation).where(
            or_(
                (Conversation.user_a_id == user["user_id"]) & (Conversation.user_b_id == receiver_id),
                (Conversation.user_a_id == receiver_id) & (Conversation.user_b_id == user["user_id"])
            )
        )
    )
    conversation = q.scalars().first()

    if not conversation:
        conversation = Conversation(user_a_id=user["user_id"], user_b_id=receiver_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    return {"conversation_public_id": conversation.public_id}



@router.get("/{conversation_public_id}/partner", response_model=dict)
async def get_conversation_partner(
    conversation_public_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    q = await db.execute(select(Conversation).where(Conversation.public_id == conversation_public_id))
    conversation = q.scalars().first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if user["user_id"] == conversation.user_a_id:
        partner_id = conversation.user_b_id
    elif user["user_id"] == conversation.user_b_id:
        partner_id = conversation.user_a_id
    else:
        raise HTTPException(status_code=403, detail="You are not part of this conversation")

    partner = await db.get(User, partner_id)
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    return {
        "id": partner.id,
        "first_name": partner.first_name,
        "last_name": partner.last_name,
        "full_name": f"{partner.first_name} {partner.last_name}",
        "profile_picture": partner.profile_picture
    }
