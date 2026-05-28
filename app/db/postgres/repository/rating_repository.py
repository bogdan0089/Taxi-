from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.models.rating_model import Rating
from app.db.postgres.repository.base_repository import BaseRepository
from app.dto.input.trip_input_dto import CreateRatingDTO


class RatingRepository(BaseRepository):
    model = Rating

    def __init__(self, session: AsyncSession):
        super().__init__(session, Rating)

    async def create_rating(self, data: CreateRatingDTO, passenger_id: int, trip_id: int) -> Rating:
        return await self.create(
            **data.model_dump(),
            passenger_id=passenger_id,
            trip_id=trip_id,
        )

    async def get_driver_ratings(self, driver_id: int) -> list[Rating]:
        result = await self.session.execute(
            select(Rating).where(Rating.driver_id == driver_id)
        )
        return result.scalars().all()

    async def get_avg_rating(self, driver_id: int) -> float:
        result = await self.session.execute(
            select(func.avg(Rating.score)).where(Rating.driver_id == driver_id)
        )
        return result.scalar() or 0.0

    async def get_by_trip_and_passenger(self, trip_id: int, passenger_id: int) -> Rating | None:
        result = await self.session.execute(
            select(Rating).where(Rating.trip_id == trip_id, Rating.passenger_id == passenger_id)
        )
        return result.scalar_one_or_none()
