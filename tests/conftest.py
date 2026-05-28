import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from app.core.config import settings


TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@localhost:5434/uber_db_test"
)

engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionMaker = async_sessionmaker(engine, expire_on_commit=False)

import app.db.postgres.session as db_module
db_module.async_session_maker = TestSessionMaker

from app.main import app


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with TestSessionMaker() as s:
        yield s


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE users, trips, rating RESTART IDENTITY CASCADE"))
    yield
