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
from app.messages.routes import router as messages_router
from app.messages.routes import users_router
from app.notification.routes import router as notification_router
from app.statistics.routes import router as statistics_router
from app.payment import routes as payment_routes
from app.auth.routes import delete_expired_unverified_users

# 1) Background cleanup task for expired consultancy profiles
@asynccontextmanager
async def lifespan(app: FastAPI):
    async def periodic_cleanup():
        await asyncio.sleep(30)  # Delay first run to let MySQL fully start
        while True:
            async for db in get_db_session():
                try:
                    await delete_expired_consultancies(db)
                    await delete_expired_unverified_users(db)
                finally:
                    await db.aclose()
                break
            await asyncio.sleep(86400)  # run every 24 hours

    # Schedule as background task instead of awaiting directly
    asyncio.create_task(periodic_cleanup())
    yield

# 2) FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# 3) CORS setup
origins = [
    "http://localhost:8080",
    # add other allowed origins if needed, e.g. prod domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # ← update for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) Preflight handler
@app.options("/{full_path:path}", include_in_schema=False)
async def preflight_handler(full_path: str):
    return Response(status_code=200)

# 5) Routers
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(consultancy_router)
app.include_router(support_router)
app.include_router(admin_user_management_router)
app.include_router(admin_routes.router)
app.include_router(appointment_router)
app.include_router(messages_router)
app.include_router(users_router)
app.include_router(notification_router)
app.include_router(statistics_router)
app.include_router(payment_routes.router)

# 6) Health check
@app.get("/", status_code=200)
def root():
    return {"message": "Backend is running"}

# 7) Static files (if any)
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")