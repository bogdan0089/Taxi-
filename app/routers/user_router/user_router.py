from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.user_repository import UserRepository
from app.services.user_service import UserService
from app.dto.input.user_input_dto import UpdateUserDTO
from app.dto.output.user_output_dto import UserOutputDTO
from app.routers.dependencies import CurrentUser

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


@router.get("/{user_id}", response_model=UserOutputDTO)
async def get_user(
    user_id: int,
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> UserOutputDTO:
    return await service.get_user(user_id, current_user.id, current_user.role)


@router.patch("/me", response_model=UserOutputDTO)
async def update_user(
    data: UpdateUserDTO,
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> UserOutputDTO:
    return await service.update_user(current_user.id, data, current_user.id, current_user.role)


@router.delete("/me", status_code=204)
async def deactivate_user(
    current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.deactivate_user(current_user.id, current_user.id, current_user.role)
