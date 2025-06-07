import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response 
from fastapi.staticfiles import StaticFiles

from app.auth.routes import router as auth_router
from app.config import settings

# 1) Ensure any missing ENV vars fallback to defaults if needed
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
os.environ.setdefault("EMAIL_FROM",         "no-reply@easyabroad.com")
os.environ.setdefault("FRONTEND_BASE_URL",  "http://localhost:8080")

app = FastAPI()

# 2) CORS: allow only your frontend origin and credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # ← your _exact_ frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{full_path:path}", include_in_schema=False)
async def preflight_handler(full_path: str):
    # Simply return 200 OK for any OPTIONS request.
    return Response(status_code=200)

# 1) Profile routing (must come after CORS so all /profile routes are covered)
from app.auth.controller import router as profile_router
app.include_router(profile_router)

# 3) Register auth router under /auth
app.include_router(auth_router, prefix="/auth")


@app.get("/", status_code=200)
def root():
    return {"message": "Backend is running"}


# 4) Mount static directory (if you have any files under backend/static)
BASE_DIR   = Path(__file__).parent.parent  # root/backend
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
