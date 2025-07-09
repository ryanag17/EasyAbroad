from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text, DateTime, CheckConstraint
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

from app.db import Base
from app.auth.models import User

class ConsultantAvailability(Base):
    __tablename__ = "consultant_availability"

    id             = Column(Integer, primary_key=True)
    consultant_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    days_of_week   = Column(JSON, nullable=False)  # e.g. [1,3,5]
    start_time     = Column(String(5), nullable=False)  # "09:30"
    end_time       = Column(String(5), nullable=False)  # "10:30"

    consultant = relationship("User", back_populates="availability")

User.availability = relationship(
    "ConsultantAvailability",
    back_populates="consultant",
    cascade="all, delete-orphan"
)

class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    upcoming = "upcoming"
    previous = "previous"
    rejected = "rejected"

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, nullable=False)
    consultant_id = Column(Integer, ForeignKey("users.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    start_time = Column(String)
    end_time = Column(String)
    reason = Column(String)
    info = Column(String, nullable=True)
    platform = Column(String)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending)
    meeting_link = Column(String, nullable=True)
    rejection_reason = Column(String, nullable=True)
    cancellation_reason = Column(String, nullable=True) 
    student = relationship("User", foreign_keys=[student_id])
    consultant = relationship("User", foreign_keys=[consultant_id])
    type = Column(String, nullable=False)

class ConsultantReview(Base):
    __tablename__ = "consultant_reviews"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, nullable=False)
    booking_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    consultant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", foreign_keys=[student_id], backref="reviews")  # Relationship to the student (User)
    consultant = relationship("User", foreign_keys=[consultant_id], backref="consultant_reviews")  # Relationship to the consultant (User)

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range'),
    )