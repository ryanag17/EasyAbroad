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
    text
)
from sqlalchemy.orm import relationship
from pydantic_settings import SettingsConfigDict
from sqlalchemy.dialects.mysql import JSON

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

    # Make country_name REQUIRED (no longer Optional)
    # Must match the NOT NULL constraint in the SQL schema
    country_name    : Optional[str] = Field(None, alias="country_name")

    birthday        : Optional[date] = None
    gender          : Optional[Literal["male","female","other"]] = None
    profile_picture : Optional[str] = None

    # If role == "admin", they may include an access_level
    access_level    : Optional[Literal["standard","super"]] = None

    # Instead of a comma-separated string, accept a list of language-IDs
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
    role            = Column(
        Enum("student","consultant","admin", name="user_role"),
        nullable=False
    )
    city            = Column(String(255), nullable=True)

    country_name = Column(String)

    birthday        = Column(Date, nullable=True)
    gender          = Column(Enum("male","female","other", name="gender"), nullable=True)
    access_level    = Column(Enum("standard","super", name="access_level"), default="standard")
    profile_picture = Column(String(255), nullable=True)
    is_active       = Column(Boolean, default=True, nullable=False)


    # Fields for “forgot password” flows
    reset_token     = Column(String(255), nullable=True)
    token_expiry    = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Relationship to refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    # Many-to-many relationship: users ↔ languages
    languages = relationship("UserLanguage", back_populates="user")


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
    country_code = Column(String(2),   nullable=False, unique=True)


class UserLanguage(Base):
    __tablename__ = "user_languages"

    user_id     = Column(Integer, ForeignKey("users.id"), primary_key=True)
    language_id = Column(Integer, ForeignKey("languages.id"), primary_key=True)

    user     = relationship("User", back_populates="languages")
    language = relationship("Language", back_populates="users")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Use INTEGER to match your MySQL DDL (id INT AUTO_INCREMENT)
    id         = Column(Integer, primary_key=True, index=True)
    token      = Column(String(64), unique=True, nullable=False, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    user       = relationship("User", back_populates="refresh_tokens")
    issued_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked    = Column(Boolean, default=False, nullable=False)

# ────────── New schema for updating the profile / IK 06.06 ──────────
from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Literal

class UserUpdateProfile(BaseModel):
    first_name   : Optional[str] = None
    last_name    : Optional[str] = None
    city         : Optional[str] = None
    country_name : Optional[str] = Field(None, alias="country_name")
    gender       : Optional[Literal["male","female","other"]] = None
    languages    : Optional[List[int]] = None

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "first_name": "Alice",
                "last_name": "Smith",
                "city": "Berlin",
                "country_name": "Germany",
                "gender": "female",
                "languages": [1, 5, 8]
            }
        }


#New schema for changing the password / IK 13.06 
class ChangePasswordRequest(BaseModel):
    old_password: constr(min_length=8)
    new_password: constr(min_length=8)

# New schema for deleting the account / IK 13.06
class DeleteAccountRequest(BaseModel):
    email: EmailStr
    password: str



# A new availability table / IK 14.06
class ConsultantAvailability(Base):
    __tablename__ = "consultant_availability"

    id             = Column(Integer, primary_key=True)
    consultant_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    days_of_week   = Column(JSON, nullable=False)  # e.g. [1,3,5]
    start_time     = Column(String(5), nullable=False)  # "09:30"
    end_time       = Column(String(5), nullable=False)  # "10:30"

    consultant     = relationship("User", back_populates="availability")

# in User model:
User.availability = relationship(
    "ConsultantAvailability",
    back_populates="consultant",
    cascade="all, delete-orphan"
)