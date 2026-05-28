from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.models.user_model import User
from app.db.postgres.repository.base_repository import BaseRepository
from app.dto.input.user_input_dto import RegisterUserDTO, UpdateUserDTO


class UserRepository(BaseRepository):
    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_active_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalars().first()

    async def create_user(self, data: RegisterUserDTO, hashed_password: str) -> User:
        return await self.create(
            **data.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
        )

    async def update_user(self, user_id: int, data: UpdateUserDTO) -> User | None:
        return await self.update(user_id, **data.model_dump(exclude_none=True))

    async def deactivate(self, user_id: int) -> User | None:
        return await self.update(user_id, is_active=False)

    async def verify_email(self, user_id: int) -> None:
        await self.update(user_id, is_verified=True)

    async def update_avg_rating(self, user_id: int, avg: float) -> None:
        await self.update(user_id, avg_rating=avg)

    async def set_payment_id(self, user_id: int, payment_id: str) -> User | None:
        return await self.update(user_id, payment_id=payment_id)

    async def get_verified_active(self, limit: int, offset: int) -> list[User]:
        result = await self.session.execute(
            select(User)
            .where(User.is_verified == True, User.is_active == True)
            .limit(limit).offset(offset)
        )
        return result.scalars().all()
