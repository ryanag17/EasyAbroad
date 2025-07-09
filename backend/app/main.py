import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response 
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio

from app.auth.routes import router as auth_router
from app.profile.routes import router as profile_router
from app.consultancy.routes import consultancy_router
from app.config import settings
from app.db import get_db_session
from app.consultancy.controller import delete_expired_consultancies
from app.support.routes import support_router
from app.admin.routes import router as admin_user_management_router
from app.admin import routes as admin_routes
from app.appointment.routes import router as appointment_router
# 1) Ensure any missing ENV vars fallback to defaults if needed
os.environ.setdefault("DB_HOST",            "127.0.0.1")
os.environ.setdefault("DB_USER",            "appuser")
os.environ.setdefault("DB_PASSWORD",        "StrongP@ssw0rd")
os.environ.setdefault("DB_NAME",            "easyabroad")
os.environ.setdefault("JWT_SECRET",         "changeme-in-prod")
os.environ.setdefault("JWT_ALGORITHM",      "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS",   "7")
os.environ.setdefault("EMAIL_PORT",         "1025")
os.environ.setdefault("EMAIL_FROM",         "no-reply@easyabroad.com")
os.environ.setdefault("FRONTEND_BASE_URL",  "http://localhost:8080")

# 2) Background cleanup task for expired consultancy profiles
@asynccontextmanager
async def lifespan(app: FastAPI):
    async def periodic_cleanup():
        while True:
            async for db in get_db_session():
                try:
                    await delete_expired_consultancies(db)
                finally:
                    await db.aclose()
                break  # exit the async generator loop after one session
            await asyncio.sleep(86400)  # every 24 hours

    asyncio.create_task(periodic_cleanup())
    yield

# 3) FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8080",
    # add other allowed origins if needed, e.g. prod domain
]

# 4) CORS: allow only your frontend origin and credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # ← wildcard for now
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# # 5) Allow all OPTIONS requests
@app.options("/{full_path:path}", include_in_schema=False)
async def preflight_handler(full_path: str):
      return Response(status_code=200)

# 6) Routers
app.include_router(profile_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(consultancy_router)
app.include_router(support_router)
app.include_router(admin_user_management_router)
app.include_router(admin_routes.router, prefix="/admin")
app.include_router(appointment_router)
# 7) Messaging endpoints (student⇄consultant only)
from app.messages.routes import router as messages_router  # ✅

app.include_router(messages_router)
from app.messages.routes import users_router
app.include_router(users_router)


from app.notification.routes import router as notification_router
app.include_router(notification_router)

from app.statistics.routes import router as statistics_router
app.include_router(statistics_router)

from app.payment import routes as payment_routes
app.include_router(payment_routes.router)


# 7) Health check
@app.get("/", status_code=200)
def root():
    return {"message": "Backend is running"}

# 8) Static files (if any)
BASE_DIR   = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")