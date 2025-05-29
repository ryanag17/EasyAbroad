from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DB_HOST:     str = Field(..., description="Database host")
    DB_USER:     str = Field(..., description="Database user")
    DB_PASSWORD: str = Field(..., description="Database password")
    DB_NAME:     str = Field(..., description="Database name")

    # JWT / Token
    JWT_SECRET:                  str = Field(..., description="Secret key for signing JWTs")
    JWT_ALGORITHM:               str = Field("HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, description="Access token lifetime in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS:   int = Field(7,  description="Refresh token lifetime in days")

    # Email
    EMAIL_HOST: str = Field(..., description="SMTP server host")
    EMAIL_PORT: int = Field(..., description="SMTP server port")
    EMAIL_FROM: str = Field(..., description="Default From address for outgoing mail")

    # Frontend
    FRONTEND_BASE_URL: str = Field(..., description="Base URL of the frontend application")

    model_config = SettingsConfigDict(env_file=None)

settings = Settings()
