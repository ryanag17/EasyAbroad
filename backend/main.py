# backend/app/main.py

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
app.include_router(auth_router, prefix="/api/auth")

@app.get("/")
def root():
    return {"message": "Backend is running"}

# Mount static files from backend/app/static
BASE_DIR   = Path(__file__).parent        # -> /app/app
STATIC_DIR = BASE_DIR / "static"          # -> /app/app/static
if not STATIC_DIR.exists():
    raise RuntimeError(f"Static directory not found: {STATIC_DIR}")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
