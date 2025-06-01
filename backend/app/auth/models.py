# backend/app/auth/models.py

from datetime import datetime, date
from typing import List, Optional, Literal
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    Date, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text as sql_text
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import SettingsConfigDict

from app.db import Base


# =====================
# Pydantic Schemas
# =====================

class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserCreate(BaseModel):
    # incoming JSON: "name" → first_name, "surname" → last_name
    first_name      : str = Field(..., alias="name")
    last_name       : str = Field(..., alias="surname")
    role            : Literal["student","consultant","admin"]
    email           : EmailStr
    password        : str

    # Merged fields (formerly in separate student/consultant tables):
    city            : Optional[str] = None
    country_name    : Optional[str] = None
    birthday        : Optional[date] = None
    gender          : Optional[Literal["male","female","other"]] = None
    profile_picture : Optional[str] = None

    # Only used if role == "admin"
    access_level    : Optional[Literal["standard","super"]] = None

    # List of language IDs
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


# =====================
# SQLAlchemy ORM Models
# =====================

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    first_name      = Column(String(255), nullable=False)
    last_name       = Column(String(255), nullable=False)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    password_hash   = Column(String(255), nullable=False)
    role            = Column(Enum("student","consultant","admin", name="user_role"), nullable=False)
    city            = Column(String(255), nullable=True)
    country_name    = Column(String(100), nullable=False)

    birthday        = Column(Date, nullable=True)
    gender          = Column(Enum("male","female","other", name="gender"), nullable=True)
    access_level    = Column(Enum("standard","super", name="access_level"), default="standard")
    profile_picture = Column(String(255), nullable=True)

    reset_token     = Column(String(255), nullable=True)
    token_expiry    = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=sql_text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationship to refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    # Many-to-many relationship for languages
    languages = relationship("UserLanguage", back_populates="user")


class Language(Base):
    __tablename__ = "languages"

    id            = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(10), unique=True, nullable=False)
    language_name = Column(String(100), nullable=False)

    users = relationship("UserLanguage", back_populates="language")


class UserLanguage(Base):
    __tablename__ = "user_languages"
    user_id     = Column(Integer, ForeignKey("users.id"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id"), primary_key=True)

    user     = relationship("User", back_populates="languages")
    language = relationship("Language", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id          = Column(Integer, primary_key=True, index=True)
    token       = Column(String(64), unique=True, nullable=False, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    user        = relationship("User", back_populates="refresh_tokens")
    issued_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at  = Column(DateTime, nullable=False)
    revoked     = Column(Boolean, default=False, nullable=False)