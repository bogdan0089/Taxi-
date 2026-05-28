from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.user_repository import UserRepository
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.dto.input.user_input_dto import RegisterUserDTO, LoginUserDTO
from app.dto.output.token_output_dto import TokenOutputDTO
from app.routers.dependencies import CurrentUser

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(session))


@router.post("/register", status_code=201)
async def register_user(
    data: RegisterUserDTO,
    service: UserService = Depends(get_user_service),
) -> dict:
    return await service.register_user(data)


@router.post("/login", response_model=TokenOutputDTO)
async def login(
    data: LoginUserDTO,
    service: UserService = Depends(get_user_service),
) -> TokenOutputDTO:
    return await service.login_user(data)


@router.get("/verify/{token}")
async def verify_user(
    token: str,
    service: UserService = Depends(get_user_service),
) -> dict:
    return await service.verify_email(token)


@router.post("/refresh/{token}")
async def refresh_access_token(token: str) -> str:
    return await AuthService.refresh_access_token(token)


@router.post("/logout")
async def logout(current_user: CurrentUser) -> dict:
    return await AuthService.logout(current_user.id)
