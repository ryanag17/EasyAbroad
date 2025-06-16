from datetime import datetime, date
from typing import Literal, List, Optional


from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Date,
    Enum,
    ForeignKey,
    text,
    LargeBinary,
    Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
from pydantic_settings import SettingsConfigDict

from app.db import Base


# =====================
# Pydantic Schemas
# =====================

class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserCreate(BaseModel):
    # Incoming JSON: "name" → first_name, "surname" → last_name
    first_name      : str   = Field(..., alias="name")
    last_name       : str   = Field(..., alias="surname")
    role            : Literal["student","consultant","admin"]
    email           : EmailStr
    password        : str

    city            : Optional[str] = None

    # Must match NOT NULL constraint
    country_name    : Optional[str] = Field(None, alias="country_name")

    birthday        : Optional[date] = None
    gender          : Optional[Literal["male","female","other"]] = None
    profile_picture : Optional[str] = None

    # If role == "admin", may include an access_level
    access_level    : Optional[Literal["standard","super"]] = None

    # Instead of comma-separated, accept list of language IDs
    languages       : Optional[List[int]] = None

    model_config = SettingsConfigDict(populate_by_name=True)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token:    str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str


# ────────── New schema for updating the profile ──────────
class UserUpdateProfile(BaseModel):
    first_name   : Optional[str] = None
    last_name    : Optional[str] = None
    city         : Optional[str] = None
    country_name : Optional[str] = Field(None, alias="country_name")
    gender       : Optional[Literal["male","female","other"]] = None
    languages    : Optional[List[int]] = None

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "first_name": "Alice",
                "last_name": "Smith",
                "city": "Berlin",
                "country_name": "Germany",
                "gender": "female",
                "languages": [1, 5, 8]
            }
        }


class ChangePasswordRequest(BaseModel):
    old_password: constr(min_length=8)
    new_password: constr(min_length=8)


class DeleteAccountRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# SQLAlchemy ORM Models
# =========================

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(255), nullable=False)
    last_name       = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    password_hash   = Column(String(255), nullable=False)
    role            = Column(Enum("student","consultant","admin", name="user_role"), nullable=False)
    city            = Column(String(255), nullable=True)
    country_name    = Column(String, nullable=False)
    birthday        = Column(Date, nullable=True)
    gender          = Column(Enum("male","female","other", name="gender"), nullable=True)
    access_level    = Column(Enum("standard","super", name="access_level"), default="standard")
    profile_picture = Column(String(255), nullable=True)

    reset_token     = Column(String(255), nullable=True)
    token_expiry    = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    languages      = relationship("UserLanguage", back_populates="user")


class Language(Base):
    __tablename__ = "languages"

    id            = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(10), unique=True, nullable=False)
    language_name = Column(String(100), nullable=False)

    users = relationship("UserLanguage", back_populates="language")


class Country(Base):
    __tablename__ = "countries"

    id           = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False, unique=True)
    country_code = Column(String(2), nullable=False, unique=True)


class UserLanguage(Base):
    __tablename__ = "user_languages"

    user_id     = Column(Integer, ForeignKey("users.id"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id"), primary_key=True)

    user     = relationship("User", back_populates="languages")
    language = relationship("Language", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id         = Column(Integer, primary_key=True, index=True)
    token      = Column(String(64), unique=True, nullable=False, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    user       = relationship("User", back_populates="refresh_tokens")
    issued_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False, nullable=False)


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

