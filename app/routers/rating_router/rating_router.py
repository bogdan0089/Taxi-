from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.rating_repository import RatingRepository
from app.db.postgres.repository.trip_repository import TripRepository
from app.db.postgres.repository.user_repository import UserRepository
from app.services.rating_service import RatingService
from app.dto.input.trip_input_dto import CreateRatingDTO
from app.dto.output.rating_output_dto import RatingOutputDTO
from app.routers.dependencies import CurrentPassenger, CurrentUser

router = APIRouter(prefix="/ratings", tags=["Ratings"])


def get_rating_service(session: AsyncSession = Depends(get_session)) -> RatingService:
    return RatingService(RatingRepository(session), TripRepository(session), UserRepository(session))


@router.post("/", response_model=RatingOutputDTO)
async def create_rating(
    trip_id: int,
    data: CreateRatingDTO,
    user: CurrentPassenger,
    service: RatingService = Depends(get_rating_service),
) -> RatingOutputDTO:
    return await service.create_rating(data, user.id, trip_id)


@router.get("/driver/{driver_id}", response_model=list[RatingOutputDTO])
async def get_driver_ratings(
    driver_id: int,
    _: CurrentUser,
    service: RatingService = Depends(get_rating_service),
) -> list[RatingOutputDTO]:
    return await service.get_driver_ratings(driver_id)


@router.get("/driver/{driver_id}/avg")
async def get_avg_rating(
    driver_id: int,
    _: CurrentUser,
    service: RatingService = Depends(get_rating_service),
) -> float:
    return await service.get_avg_rating(driver_id)
