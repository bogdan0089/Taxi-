from app.db.postgres.repository.rating_repository import RatingRepository
from app.db.postgres.repository.trip_repository import TripRepository
from app.db.postgres.repository.user_repository import UserRepository
from app.dto.input.trip_input_dto import CreateRatingDTO
from app.dto.output.rating_output_dto import RatingOutputDTO
from app.core.exceptions import (
    TripNotFoundError,
    TripStatusError,
    UserNotFoundError,
    ForbiddenStatus,
    RatingAlreadyExistsError,
    TripsNotFoundError,
)
from app.core.redis import redis_client
from app.enums.status_enum import Status
from pydantic import TypeAdapter

_ratings_adapter = TypeAdapter(list[RatingOutputDTO])


class RatingService:

    def __init__(self, rating_repo: RatingRepository, trip_repo: TripRepository, user_repo: UserRepository):
        self.rating_repo = rating_repo
        self.trip_repo = trip_repo
        self.user_repo = user_repo

    async def create_rating(self, data: CreateRatingDTO, passenger_id: int, trip_id: int) -> RatingOutputDTO:
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError(trip_id)
        if trip.status != Status.COMPLETED:
            raise TripStatusError(trip_id)
        if trip.passenger_id != passenger_id:
            raise ForbiddenStatus(trip_id)
        existing = await self.rating_repo.get_by_trip_and_passenger(trip_id, passenger_id)
        if existing:
            raise RatingAlreadyExistsError()
        rating = await self.rating_repo.create_rating(data, passenger_id, trip_id)
        avg = await self.rating_repo.get_avg_rating(data.driver_id)
        await self.user_repo.update_avg_rating(data.driver_id, avg)
        await redis_client.delete(f"driver:{data.driver_id}")
        return RatingOutputDTO.model_validate(rating)

    async def get_driver_ratings(self, driver_id: int) -> list[RatingOutputDTO]:
        cached = await redis_client.get(f"driver_ratings:{driver_id}")
        if cached:
            return _ratings_adapter.validate_json(cached)
        driver = await self.user_repo.get_active_by_id(driver_id)
        if not driver:
            raise UserNotFoundError(driver_id)
        ratings = await self.rating_repo.get_driver_ratings(driver_id)
        if not ratings:
            raise TripsNotFoundError()
        validated = _ratings_adapter.validate_python(ratings)
        await redis_client.set(f"driver_ratings:{driver_id}", _ratings_adapter.dump_json(validated), ex=60)
        return validated

    async def get_avg_rating(self, driver_id: int) -> float:
        cached = await redis_client.get(f"driver:{driver_id}")
        if cached:
            return float(cached)
        driver = await self.user_repo.get_active_by_id(driver_id)
        if not driver:
            raise UserNotFoundError(driver_id)
        avg = await self.rating_repo.get_avg_rating(driver_id)
        await redis_client.set(f"driver:{driver_id}", str(avg), ex=300)
        return avg
