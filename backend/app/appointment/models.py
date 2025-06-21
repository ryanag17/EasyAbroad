from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum 
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
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
    student = relationship("User", foreign_keys=[student_id])
    consultant = relationship("User", foreign_keys=[consultant_id])