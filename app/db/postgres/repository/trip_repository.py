from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.models.trip_model import Trip
from app.db.postgres.repository.base_repository import BaseRepository
from app.dto.input.trip_input_dto import TripCreateDTO
from app.enums.status_enum import Status


class TripRepository(BaseRepository):
    model = Trip

    def __init__(self, session: AsyncSession):
        super().__init__(session, Trip)

    async def create_trip(self, data: TripCreateDTO, passenger_id: int, price: float) -> Trip:
        return await self.create(
            **data.model_dump(),
            passenger_id=passenger_id,
            price=price,
        )

    async def get_available(self, limit: int, offset: int) -> list[Trip]:
        result = await self.session.execute(
            select(Trip).where(Trip.status == Status.WAITING).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_my_trips(self, user_id: int, limit: int, offset: int) -> list[Trip]:
        result = await self.session.execute(
            select(Trip)
            .where((Trip.passenger_id == user_id) | (Trip.driver_id == user_id))
            .limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def accept_trip(self, trip_id: int, driver_id: int) -> Trip | None:
        await self.session.execute(
            update(Trip)
            .where(Trip.id == trip_id)
            .values(driver_id=driver_id, status=Status.IN_PROGRESS)
        )
        await self.session.commit()
        return await self.get_by_id(trip_id)
