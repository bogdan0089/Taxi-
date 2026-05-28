from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.user_repository import UserRepository
from app.services.user_service import UserService
from app.routers.dependencies import CurrentUser

router = APIRouter(prefix="/payment", tags=["Payment"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


@router.post("/method")
async def save_payment_method(
    data: dict,
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> dict:
    payment_id = data.get("payment_id")
    return await service.save_payment_id(current_user.id, payment_id)
