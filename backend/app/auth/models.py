from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Date, Enum as PgEnum, Boolean,
    DateTime, ForeignKey, text
)
from sqlalchemy.orm import relationship
from app.db import Base

import enum

class UserStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(PgEnum("student", "consultant", "admin", name="user_role"), nullable=False)
    city = Column(String(255), nullable=True)
    country_name = Column(String, nullable=False)
    birthday = Column(Date, nullable=True)
    gender = Column(PgEnum("male", "female", "other", name="gender"), nullable=True)
    access_level = Column(PgEnum("standard", "super", name="access_level"), default="standard")
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(PgEnum(UserStatusEnum, name="user_status_enum"), default=UserStatusEnum.active, nullable=False)

    reset_token = Column(String(255), nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    languages = relationship("UserLanguage", back_populates="user")


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String(10), unique=True, nullable=False)
    language_name = Column(String(100), nullable=False)

    users = relationship("UserLanguage", back_populates="language")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False, unique=True)
    country_code = Column(String(2), nullable=False, unique=True)


class UserLanguage(Base):
    __tablename__ = "user_languages"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id"), primary_key=True)

    user = relationship("User", back_populates="languages")
    language = relationship("Language", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="refresh_tokens")
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
