from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

async_engine = create_async_engine(settings.DATABASE_URL)

async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
