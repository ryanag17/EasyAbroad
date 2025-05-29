# backend/app/main.py

import os

# ── 1) Programmatically seed os.environ with defaults ────────────────────────
#    (these will only apply if no real ENV var is already set)
os.environ.setdefault("DB_HOST",            "127.0.0.1")
os.environ.setdefault("DB_USER",            "appuser")
os.environ.setdefault("DB_PASSWORD",        "StrongP@ssw0rd")
os.environ.setdefault("DB_NAME",            "easyabroad")

os.environ.setdefault("JWT_SECRET",         "changeme-in-prod")
os.environ.setdefault("JWT_ALGORITHM",      "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS",   "7")

os.environ.setdefault("EMAIL_HOST",         "smtp.mailhog.internal")
os.environ.setdefault("EMAIL_PORT",         "1025")
os.environ.setdefault("EMAIL_USERNAME",     "anyuser")
os.environ.setdefault("EMAIL_PASSWORD",     "anypass")
os.environ.setdefault("EMAIL_FROM",         "no-reply@easyabroad.com")

os.environ.setdefault("FRONTEND_BASE_URL",  "http://localhost:8080")


from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.auth.routes import router as auth_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register your API router
app.include_router(auth_router, prefix="/auth")

@app.get("/")
def root():
    return {"message": "Backend is running"}

# ── MOUNT STATIC FILES ────────────────────────────────────────────────────────
# Your Dockerfile copies `static/` into /app/static, not /app/app/static,
# so we must point one level up from this file’s directory:
BASE_DIR   = Path(__file__).parent.parent  # -> /app
STATIC_DIR = BASE_DIR / "static"           # -> /app/static

if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
