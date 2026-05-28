from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.trip_repository import TripRepository
from app.db.postgres.repository.user_repository import UserRepository
from app.services.trip_service import TripService
from app.dto.input.trip_input_dto import TripCreateDTO
from app.dto.output.trip_output_dto import TripOutputDTO
from app.enums.status_enum import Status
from app.routers.dependencies import CurrentUser, CurrentPassenger, CurrentDriver

router = APIRouter(prefix="/trips", tags=["Trips"])


def get_trip_service(session: AsyncSession = Depends(get_session)) -> TripService:
    return TripService(TripRepository(session), UserRepository(session))


@router.post("/", response_model=TripOutputDTO)
async def create_trip(
    data: TripCreateDTO,
    user: CurrentPassenger,
    service: TripService = Depends(get_trip_service),
) -> TripOutputDTO:
    return await service.create_trip(data, user.id)


@router.get("/available", response_model=list[TripOutputDTO])
async def get_available(
    _: CurrentDriver,
    limit: int = 10,
    offset: int = 0,
    service: TripService = Depends(get_trip_service),
) -> list[TripOutputDTO]:
    return await service.get_available(limit, offset)


@router.get("/my", response_model=list[TripOutputDTO])
async def get_my_trips(
    user: CurrentUser,
    limit: int = 10,
    offset: int = 0,
    service: TripService = Depends(get_trip_service),
) -> list[TripOutputDTO]:
    return await service.get_my_trips(user.id, limit, offset)


@router.get("/{trip_id}", response_model=TripOutputDTO)
async def get_trip(
    trip_id: int,
    _: CurrentUser,
    service: TripService = Depends(get_trip_service),
) -> TripOutputDTO:
    return await service.get_trip(trip_id)


@router.post("/{trip_id}/accept", response_model=TripOutputDTO)
async def accept_trip(
    trip_id: int,
    user: CurrentDriver,
    service: TripService = Depends(get_trip_service),
) -> TripOutputDTO:
    return await service.update_status(trip_id, Status.IN_PROGRESS, user.id)


@router.post("/{trip_id}/complete", response_model=TripOutputDTO)
async def complete_trip(
    trip_id: int,
    _: CurrentDriver,
    service: TripService = Depends(get_trip_service),
) -> TripOutputDTO:
    return await service.update_status(trip_id, Status.COMPLETED)


@router.post("/{trip_id}/cancel", response_model=TripOutputDTO)
async def cancel_trip(
    trip_id: int,
    _: CurrentUser,
    service: TripService = Depends(get_trip_service),
) -> TripOutputDTO:
    return await service.update_status(trip_id, Status.CANCELLED)
