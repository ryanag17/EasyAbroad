from datetime import date
from typing import Literal, List, Optional
from pydantic import BaseModel, EmailStr, Field, constr
from pydantic_settings import SettingsConfigDict



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

