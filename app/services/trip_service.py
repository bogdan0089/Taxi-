from app.db.postgres.repository.trip_repository import TripRepository
from app.db.postgres.repository.user_repository import UserRepository
from app.dto.input.trip_input_dto import TripCreateDTO
from app.dto.output.trip_output_dto import TripOutputDTO
from app.core.exceptions import (
    TripNotFoundError,
    TripsNotFoundError,
    TripStatusError,
    DriversNotFoundError,
    UserNotFoundError,
    PaymentMethodNotFoundError,
)
from app.core.redis import redis_client
from app.enums.status_enum import Status
from app.services.stripe_service import StripeService
from app.utils.price_calculator import price_calculate
from pydantic import TypeAdapter

_trips_adapter = TypeAdapter(list[TripOutputDTO])

ALLOWED_TRANSITIONS = {
    Status.WAITING:     [Status.IN_PROGRESS, Status.CANCELLED],
    Status.IN_PROGRESS: [Status.COMPLETED, Status.CANCELLED],
    Status.COMPLETED:   [],
    Status.CANCELLED:   [],
}


class TripService:

    def __init__(self, trip_repo: TripRepository, user_repo: UserRepository):
        self.trip_repo = trip_repo
        self.user_repo = user_repo

    async def create_trip(self, data: TripCreateDTO, passenger_id: int) -> TripOutputDTO:
        price = price_calculate(data.pickup_lat, data.pickup_lon, data.dropoff_lat, data.dropoff_lon)
        trip = await self.trip_repo.create_trip(data, passenger_id, price)
        drivers = await redis_client.georadius("drivers", data.pickup_lon, data.pickup_lat, 5, "km")
        if not drivers:
            raise DriversNotFoundError()
        driver_id = int(drivers[0].decode().split(":")[1])
        trip = await self.trip_repo.accept_trip(trip.id, driver_id)
        return TripOutputDTO.model_validate(trip)

    async def get_trip(self, trip_id: int) -> TripOutputDTO:
        cached = await redis_client.get(f"trip:{trip_id}")
        if cached:
            return TripOutputDTO.model_validate_json(cached)
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError(trip_id)
        output = TripOutputDTO.model_validate(trip)
        await redis_client.set(f"trip:{trip_id}", output.model_dump_json(), ex=300)
        return output

    async def get_available(self, limit: int, offset: int) -> list[TripOutputDTO]:
        trips = await self.trip_repo.get_available(limit, offset)
        if not trips:
            raise TripsNotFoundError()
        return [TripOutputDTO.model_validate(t) for t in trips]

    async def get_my_trips(self, user_id: int, limit: int, offset: int) -> list[TripOutputDTO]:
        trips = await self.trip_repo.get_my_trips(user_id, limit, offset)
        if not trips:
            raise TripsNotFoundError()
        return [TripOutputDTO.model_validate(t) for t in trips]

    async def get_all_trips(self, limit: int = 100, offset: int = 0) -> list[TripOutputDTO]:
        cached = await redis_client.get("admin:trips")
        if cached:
            return _trips_adapter.validate_json(cached)
        trips = await self.trip_repo.get_all(limit, offset)
        if not trips:
            raise TripsNotFoundError()
        output = [TripOutputDTO.model_validate(t) for t in trips]
        await redis_client.set("admin:trips", _trips_adapter.dump_json(output), ex=60)
        return output

    async def update_status(self, trip_id: int, new_status: Status, driver_id: int | None = None) -> TripOutputDTO:
        trip = await self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundError(trip_id)
        if new_status not in ALLOWED_TRANSITIONS[trip.status]:
            raise TripStatusError(trip_id)
        if new_status == Status.IN_PROGRESS and driver_id:
            updated = await self.trip_repo.accept_trip(trip_id, driver_id)
        else:
            updated = await self.trip_repo.update(trip_id, status=new_status)
        if new_status == Status.COMPLETED:
            user = await self.user_repo.get_active_by_id(trip.passenger_id)
            if not user:
                raise UserNotFoundError(trip.passenger_id)
            if not user.payment_id:
                raise PaymentMethodNotFoundError(user.id)
            await StripeService.charge(trip.price, user.payment_id)
        async for key in redis_client.scan_iter("trip*"):
            await redis_client.unlink(key)
        return TripOutputDTO.model_validate(updated)
