from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.user_repository import UserRepository
from app.db.postgres.repository.trip_repository import TripRepository
from app.services.user_service import UserService
from app.services.trip_service import TripService
from app.dto.output.user_output_dto import UserOutputDTO
from app.dto.output.trip_output_dto import TripOutputDTO
from app.routers.dependencies import CurrentAdmin

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


def get_trip_service(session: AsyncSession = Depends(get_session)) -> TripService:
    return TripService(TripRepository(session), UserRepository(session))


@router.get("/users", response_model=list[UserOutputDTO])
async def get_all_users(
    _: CurrentAdmin,
    limit: int = 100,
    offset: int = 0,
    service: UserService = Depends(get_user_service),
) -> list[UserOutputDTO]:
    return await service.get_all_users(limit, offset)


@router.get("/trips", response_model=list[TripOutputDTO])
async def get_all_trips(
    _: CurrentAdmin,
    limit: int = 100,
    offset: int = 0,
    service: TripService = Depends(get_trip_service),
) -> list[TripOutputDTO]:
    return await service.get_all_trips(limit, offset)


@router.get("/active/verified", response_model=list[UserOutputDTO])
async def get_active_verified(
    _: CurrentAdmin,
    limit: int = 100,
    offset: int = 0,
    service: UserService = Depends(get_user_service),
) -> list[UserOutputDTO]:
    return await service.get_verified_active(limit, offset)
