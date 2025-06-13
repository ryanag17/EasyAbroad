from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.config import settings
from collections.abc import AsyncGenerator

# Compose the MySQL URL for aiomysql
DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}"
    f":{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"
)

# 1) Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# 2) Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3) Base class for ORM models
Base = declarative_base()

# Dependency used in routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 🔧 Direct session getter for background tasks
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
