from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:

    def __init__(self, session: AsyncSession, model):
        self.session = session
        self.model = model

    async def get_by_id(self, record_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        return result.scalars().first()

    async def get_all(self, limit: int = 10, offset: int = 0):
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def filter_by(self, **kwargs):
        """Get records filtered by any model fields."""
        result = await self.session.execute(
            select(self.model).filter_by(**kwargs)
        )
        return result.scalars().all()

    async def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.session.add(instance)
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except IntegrityError:
            await self.session.rollback()
            raise

    async def update(self, record_id: int, **kwargs):
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        instance = result.scalars().first()
        if not instance:
            return None
        for field, value in kwargs.items():
            setattr(instance, field, value)
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def delete(self, record_id: int) -> bool:
        result = await self.session.execute(
            select(self.model).where(self.model.id == record_id)
        )
        instance = result.scalars().first()
        if not instance:
            return False
        try:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        except SQLAlchemyError:
            await self.session.rollback()
            raise
