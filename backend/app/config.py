# app/config.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ─── Database ────────────────────────────────────────────────────────────────
    DB_HOST:     str = Field(
        "127.0.0.1",
        description="Database host (default for local dev)"
    )
    DB_USER:     str = Field(
        "appuser",
        description="Database user (default for local dev)"
    )
    DB_PASSWORD: str = Field(
        "StrongP@ssw0rd",
        description="Database password (default for local dev)"
    )
    DB_NAME:     str = Field(
        "easyabroad",
        description="Database name (default for local dev)"
    )

    # ─── JWT / Token ─────────────────────────────────────────────────────────────
    JWT_SECRET:                  str = Field(
        "changeme-in-prod",
        description="Secret key for signing JWTs (default for local dev)"
    )
    JWT_ALGORITHM:               str = Field(
        "HS256",
        description="JWT signing algorithm (default HS256)"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        10080,
        description="Access token lifetime in minutes (default 15)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS:   int = Field(
        7,
        description="Refresh token lifetime in days (default 7)"
    )

    # ─── Email ───────────────────────────────────────────────────────────────────
    EMAIL_HOST: str = Field(
        "smtp.mailhog.internal",
        description="SMTP server host (default for local dev)"
    )
    EMAIL_PORT: int = Field(
        1025,
        description="SMTP server port (default 1025 for MailHog)"
    )
    EMAIL_FROM: str = Field(
        "no-reply@easyabroad.com",
        description="Default From address for outgoing mail"
    )
    EMAIL_USER: str = Field(
        "no-reply@easyabroad.com",
        description="SMTP username (usually your email address)"
    )
    EMAIL_PASSWORD: str = Field(
        "",
        description="SMTP password for your email account"
    )
    # ─── Frontend ─────────────────────────────────────────────────────────────────
    FRONTEND_BASE_URL: str = Field(
        "http://localhost:8080",
        description="Base URL of the frontend application (default localhost:8080)"
    )

    # ─── Tell Pydantic not to look for any .env file ───────────────────────────────
    model_config = SettingsConfigDict(env_file=None)


# Instantiate the settings once so that `from app.config import settings` works
settings = Settings()
