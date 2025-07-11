from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ─── Database ──────────────────────────────
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # ─── JWT / Token ──────────────────────────
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # ─── Email ────────────────────────────────
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_FROM: str
    EMAIL_USER: str
    EMAIL_PASSWORD: str

    # ─── Frontend ─────────────────────────────
    FRONTEND_BASE_URL: str

    # ─── Payment ─────────────────────────────
    STRIPE_SECRET_KEY: str

    # ─── Enable .env support (optional for local dev) ──
    model_config = SettingsConfigDict(env_file=".env")

# Instantiate once
settings = Settings()