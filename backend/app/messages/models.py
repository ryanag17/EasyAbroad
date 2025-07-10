from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, ForeignKey, DateTime, LargeBinary, String, Boolean, Index, JSON
from app.db import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_a_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_conversations_users", "user_a_id", "user_b_id"),
    )

class Message(Base):
    __tablename__ = "messages"

    id                = Column(Integer, primary_key=True, index=True)
    public_id         = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    sender_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id   = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    booking_id        = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=True)
    encrypted_message = Column(LargeBinary(512), nullable=False)
    encryption_iv     = Column(LargeBinary(16), nullable=False)
    is_reported       = Column(Boolean, default=False)
    reported_at       = Column(DateTime, nullable=True)
    sent_at           = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at        = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=365 * 3), nullable=False)
    hidden_for_user_ids = Column(JSON, default=list)    

    __table_args__ = (
        Index("ix_messages_booking", "booking_id"),
        Index("ix_messages_sender_receiver", "sender_id", "receiver_id"),
        Index("ix_messages_sent_at", "sent_at"),
        Index("ix_messages_expires_at", "expires_at"),
        Index("ix_messages_conversation_id", "conversation_id"),
    )