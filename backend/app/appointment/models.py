from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

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
