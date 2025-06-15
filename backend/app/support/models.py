from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum as PyEnum

class TicketStatus(str, PyEnum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus, name="status_enum"), default=TicketStatus.open)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    messages = relationship("SupportTicketMessage", back_populates="ticket", cascade="all, delete")


class SupportTicketMessage(Base):
    __tablename__ = "support_ticket_messages"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())

    ticket = relationship("SupportTicket", back_populates="messages")

