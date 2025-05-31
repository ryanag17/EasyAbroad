from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import (
    Column, BigInteger, String, DateTime, Boolean,
    ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from app.db import Base

# === 1) Pydantic Schemas ===

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class UserCreate(BaseModel):
    # The front-end will send JSON keys "name" / "surname",
    # but we map those to first_name / last_name internally:
    first_name: str = Field(..., alias="name")
    last_name:  str = Field(..., alias="surname")
    role:       str  # "student", "consultant", or "admin"
    email:      EmailStr
    password:   str

    # This tells Pydantic: populate first_name from JSON key "name", etc.
    model_config = ConfigDict(populate_by_name=True)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token:    str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str


# === 2) SQLAlchemy ORM Models ===

class User(Base):
    __tablename__ = "users"

    id            = Column(BigInteger, primary_key=True, index=True)
    first_name    = Column(String(100), nullable=False)
    last_name     = Column(String(100), nullable=False)
    email         = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    reset_token   = Column(String(255), nullable=True)
    token_expiry  = Column(DateTime, nullable=True)
    role          = Column(String(20), nullable=False)
    city          = Column(String(255), nullable=True)
    country       = Column(String(255), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # One‐to‐one relationships to Student and Consultant:
    student        = relationship("Student",      back_populates="user", cascade="all, delete-orphan", uselist=False)
    consultant     = relationship("Consultant",   back_populates="user", cascade="all, delete-orphan", uselist=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    user_id         = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    birthday        = Column(DateTime, nullable=True)
    gender          = Column(Enum('male','female','other', name='gender'), nullable=True)
    languages       = Column(Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)

    user = relationship("User", back_populates="student")


class Consultant(Base):
    __tablename__ = "consultants"
    user_id             = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    birthday            = Column(DateTime, nullable=True)
    gender              = Column(Enum('male','female','other', name='gender'), nullable=True)
    focus               = Column(Enum('study','intern','both', name='focus'), nullable=True)
    languages           = Column(Text, nullable=True)
    place_of_work       = Column(String(255), nullable=True)
    proof_of_education  = Column(String(255), nullable=True)
    education_period    = Column(DateTime, nullable=True)
    proof_of_work       = Column(String(255), nullable=True)
    internship_period   = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consultant")


class Admin(Base):
    __tablename__ = "admins"
    user_id     = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    access_level= Column(Enum('standard','super', name='access_level'), default='standard')
    notes       = Column(Text, nullable=True)

    user = relationship("User")


class Education(Base):
    __tablename__ = "Education"
    user_id             = Column(BigInteger, ForeignKey("consultants.user_id"), primary_key=True)
    city_of_study       = Column(String(255), nullable=True)
    country_of_study    = Column(String(255), nullable=True)
    university_name     = Column(String(255), nullable=True)
    study_program       = Column(String(255), nullable=True)
    education_start     = Column(DateTime, nullable=True)
    education_finish    = Column(DateTime, nullable=True)
    proof_of_education  = Column(String(255), nullable=True)
    accommodation       = Column(Boolean, nullable=True)
    social_life         = Column(Boolean, nullable=True)
    uni_info            = Column(Boolean, nullable=True)
    travel_info         = Column(Boolean, nullable=True)
    is_verified         = Column(Boolean, nullable=True)
    verified_by         = Column(BigInteger, ForeignKey("admins.user_id"), nullable=True)
    verified_at         = Column(DateTime, nullable=True)


class Internship(Base):
    __tablename__ = "Internship"
    user_id               = Column(BigInteger, ForeignKey("consultants.user_id"), primary_key=True)
    city_of_internship    = Column(String(255), nullable=True)
    country_of_internship = Column(String(255), nullable=True)
    company_name          = Column(String(255), nullable=True)
    internship_position   = Column(String(255), nullable=True)
    proof_of_internship   = Column(String(255), nullable=True)
    accommodation         = Column(Boolean, nullable=True)
    social_life           = Column(Boolean, nullable=True)
    company_info          = Column(Boolean, nullable=True)
    travel_info           = Column(Boolean, nullable=True)
    is_verified           = Column(Boolean, nullable=True)
    verified_by           = Column(BigInteger, ForeignKey("admins.user_id"), nullable=True)
    verified_at           = Column(DateTime, nullable=True)


class Calendar(Base):
    __tablename__ = "Calendar"
    user_id               = Column(BigInteger, ForeignKey("consultants.user_id"), primary_key=True)
    available_day         = Column(String(255), nullable=True)
    available_time_start  = Column(DateTime, nullable=True)
    available_time_end    = Column(DateTime, nullable=True)


class Booking(Base):
    __tablename__ = "bookings"
    id                  = Column(BigInteger, primary_key=True, index=True)
    student_id          = Column(BigInteger, ForeignKey("students.user_id"), nullable=False)
    consultant_id       = Column(BigInteger, ForeignKey("consultants.user_id"), nullable=False)
    status              = Column(Enum('pending','confirmed','cancelled','completed', name='status'), nullable=False)
    booked_at           = Column(DateTime, nullable=True)
    scheduled_time      = Column(DateTime, nullable=True)
    duration_minutes    = Column(BigInteger, nullable=True)

    student    = relationship("Student")
    consultant = relationship("Consultant")


class Session(Base):
    __tablename__ = "sessions"
    id          = Column(BigInteger, primary_key=True, index=True)
    booking_id  = Column(BigInteger, ForeignKey("bookings.id"))
    video_link  = Column(String(255), nullable=True)
    started_at  = Column(DateTime, nullable=True)
    ended_at    = Column(DateTime, nullable=True)
    notes       = Column(Text, nullable=True)

    booking     = relationship("Booking")


class Message(Base):
    __tablename__ = "messages"
    id           = Column(BigInteger, primary_key=True, index=True)
    sender_id    = Column(BigInteger, ForeignKey("users.id"))
    receiver_id  = Column(BigInteger, ForeignKey("users.id"))
    booking_id   = Column(BigInteger, ForeignKey("bookings.id"))
    message_text = Column(Text, nullable=True)
    sent_at      = Column(DateTime, nullable=True)

    sender    = relationship("User", foreign_keys=[sender_id])
    receiver  = relationship("User", foreign_keys=[receiver_id])
    booking   = relationship("Booking")


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id            = Column(BigInteger, primary_key=True, index=True)
    user_id       = Column(BigInteger, ForeignKey("users.id"))
    subject       = Column(String(255), nullable=True)
    description   = Column(Text, nullable=True)
    status        = Column(Enum('open','in_progress','resolved','closed', name='ticket_status'), nullable=True)
    created_at    = Column(DateTime, nullable=True)
    updated_at    = Column(DateTime, nullable=True)
    resolved_by   = Column(BigInteger, ForeignKey("admins.user_id"), nullable=True)
    resolved_at   = Column(DateTime, nullable=True)

    user      = relationship("User")
    resolver  = relationship("Admin", foreign_keys=[resolved_by])


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id                = Column(BigInteger, primary_key=True, index=True)
    user_id           = Column(BigInteger, ForeignKey("users.id"))
    document_name     = Column(String(255), nullable=True)
    document_type     = Column(Enum('company','school', name='doc_type'), nullable=True)
    upload_date       = Column(DateTime, nullable=True)
    verification_date = Column(DateTime, nullable=True)
    is_valid          = Column(Boolean, nullable=True)

    user = relationship("User")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id          = Column(BigInteger, primary_key=True, index=True)
    token       = Column(String(64), unique=True, nullable=False, index=True)
    user_id     = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    issued_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at  = Column(DateTime, nullable=False)
    revoked     = Column(Boolean, default=False, nullable=False)

    user        = relationship("User", back_populates="refresh_tokens")
