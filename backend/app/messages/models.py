from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, LargeBinary, Index
from app.db import Base



class Message(Base):
    __tablename__ = "messages"

    id                = Column(Integer, primary_key=True, index=True)
    sender_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id        = Column(Integer, nullable=True)
    encrypted_message = Column(LargeBinary(512), nullable=False)
    encryption_iv     = Column(LargeBinary(16),  nullable=False)
    sent_at           = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_messages_booking", "booking_id"),
        Index("ix_messages_sender_receiver", "sender_id", "receiver_id"),
        Index("ix_messages_sent_at", "sent_at"),
    )