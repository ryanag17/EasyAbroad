from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base
import uuid

class Education(Base):
    __tablename__ = "Education"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    public_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    city_of_study = Column(String(255))
    country_of_study = Column(String(100), ForeignKey("countries.country_name", ondelete="RESTRICT", onupdate="CASCADE"))
    university_name = Column(String(255))
    course_name = Column(String(255))
    education_start = Column(DateTime)
    education_finish = Column(DateTime)
    proof_of_education = Column(String(255))
    
    accommodation = Column(Boolean, default=False)
    social_life = Column(Boolean, default=False)
    uni_info = Column(Boolean, default=False)
    travel_info = Column(Boolean, default=False)

    zoom = Column(Boolean, default=False)
    microsoft_teams = Column(Boolean, default=False)
    google_meet = Column(Boolean, default=False)
    apple_facetime = Column(Boolean, default=False)

    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    status = Column(String(20), nullable=False, default="pending")  # Options: 'pending', 'accepted', 'rejected'
    short_note = Column(Text, nullable=True)

    user = relationship("User", back_populates="education", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])


from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base
import uuid

class Internship(Base):
    __tablename__ = "Internship"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    public_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    city_of_internship = Column(String(255))
    country_of_internship = Column(String(100), ForeignKey("countries.country_name", ondelete="RESTRICT", onupdate="CASCADE"))
    company_name = Column(String(255))
    department_name = Column(String(255))
    internship_start = Column(DateTime)
    internship_finish = Column(DateTime)
    proof_of_internship = Column(String(255))

    accommodation = Column(Boolean, default=False)
    social_life = Column(Boolean, default=False)
    company_info = Column(Boolean, default=False)
    travel_info = Column(Boolean, default=False)

    zoom = Column(Boolean, default=False)
    microsoft_teams = Column(Boolean, default=False)
    google_meet = Column(Boolean, default=False)
    apple_facetime = Column(Boolean, default=False)

    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    status = Column(String(20), nullable=False, default="pending")
    short_note = Column(Text, nullable=True)

    user = relationship("User", back_populates="internship", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by])
