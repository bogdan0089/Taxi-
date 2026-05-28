from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres.session import get_session
from app.db.postgres.repository.user_repository import UserRepository
from app.db.postgres.models.user_model import User
from app.services.auth_service import AuthService
from app.core.exceptions import UserNotFoundError, PermissionDeniedError
from app.enums.role_enum import Role


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    user_id = AuthService.decode_token(token)
    repo = UserRepository(session)
    user = await repo.get_active_by_id(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_passenger(user: CurrentUser) -> User:
    if user.role != Role.PASSENGER:
        raise PermissionDeniedError()
    return user


CurrentPassenger = Annotated[User, Depends(require_passenger)]


async def require_driver(user: CurrentUser) -> User:
    if user.role != Role.DRIVER:
        raise PermissionDeniedError()
    return user


CurrentDriver = Annotated[User, Depends(require_driver)]


async def require_admin(user: CurrentUser) -> User:
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return user


CurrentAdmin = Annotated[User, Depends(require_admin)]
