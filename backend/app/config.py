# backend/app/config.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DB_HOST:     str = Field(..., description="Database host")
    DB_USER:     str = Field(..., description="Database user")
    DB_PASSWORD: str = Field(..., description="Database password")
    DB_NAME:     str = Field(..., description="Database name")

    # JWT
    JWT_SECRET:    str = Field(..., description="Secret key for signing JWTs")
    JWT_ALGORITHM: str = Field("HS256", description="JWT signing algorithm")

    # Email
    EMAIL_HOST: str = Field(..., description="SMTP server host")
    EMAIL_PORT: int = Field(..., description="SMTP server port")
    EMAIL_FROM: str = Field(..., description="Default From address for outgoing mail")

    # Frontend
    FRONTEND_BASE_URL: str = Field(..., description="Base URL of the frontend application")

    # Pydantic-v2 settings config — do not load any .env
    model_config = SettingsConfigDict(env_file=None)

# Instantiate — will error immediately if any required var is missing
settings = Settings()
