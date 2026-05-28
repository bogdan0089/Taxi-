import uuid
from pydantic import TypeAdapter
from app.db.postgres.repository.user_repository import UserRepository
from app.dto.input.user_input_dto import RegisterUserDTO, UpdateUserDTO, LoginUserDTO
from app.dto.output.user_output_dto import UserOutputDTO
from app.dto.output.token_output_dto import TokenOutputDTO
from app.core.exceptions import (
    UserAlreadyError,
    UserNotFoundError,
    UsersNotFoundError,
    PasswordError,
    TokenInvalidError,
    PermissionDeniedError,
)
from app.core.redis import redis_client
from app.services.auth_service import AuthService
from app.enums.role_enum import Role
from app.utils.hash import hash_password, verify_password

_users_adapter = TypeAdapter(list[UserOutputDTO])


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, data: RegisterUserDTO) -> dict:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise UserAlreadyError(email=data.email)
        hashed = hash_password(data.password)
        user = await self.repo.create_user(data, hashed)
        token = str(uuid.uuid4())
        await redis_client.set(f"verify:{token}", user.id, ex=86400)
        return {"message": "Registration successful. Please verify your email."}

    async def login_user(self, data: LoginUserDTO) -> TokenOutputDTO:
        user = await self.repo.get_by_email(data.email)
        if not user:
            raise UserNotFoundError(email=data.email)
        if not verify_password(data.password, user.hashed_password):
            raise PasswordError()
        access_token = AuthService.create_access_token(user.id)
        refresh_token = await AuthService.create_refresh_token(user.id)
        return TokenOutputDTO(access_token=access_token, refresh_token=refresh_token)

    async def get_user(self, user_id: int, current_user_id: int, current_role: Role) -> UserOutputDTO:
        cached = await redis_client.get(f"user:{user_id}")
        if cached:
            return UserOutputDTO.model_validate_json(cached)
        user = await self.repo.get_active_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if current_user_id != user_id and current_role != Role.ADMIN:
            raise PermissionDeniedError()
        output = UserOutputDTO.model_validate(user)
        await redis_client.set(f"user:{user_id}", output.model_dump_json(), ex=60)
        return output

    async def update_user(self, user_id: int, data: UpdateUserDTO, current_user_id: int, current_role: Role) -> UserOutputDTO:
        if user_id != current_user_id and current_role != Role.ADMIN:
            raise PermissionDeniedError()
        user = await self.repo.update_user(user_id, data)
        if not user:
            raise UserNotFoundError(user_id)
        return UserOutputDTO.model_validate(user)

    async def deactivate_user(self, user_id: int, current_user_id: int, current_role: Role) -> None:
        if user_id != current_user_id and current_role != Role.ADMIN:
            raise PermissionDeniedError()
        user = await self.repo.deactivate(user_id)
        if not user:
            raise UserNotFoundError(user_id)

    async def verify_email(self, token: str) -> dict:
        user_id_bytes = await redis_client.get(f"verify:{token}")
        if not user_id_bytes:
            raise TokenInvalidError()
        user_id = int(user_id_bytes.decode())
        user = await self.repo.get_active_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        await self.repo.verify_email(user_id)
        await redis_client.delete(f"verify:{token}")
        return {"message": "Email verified successfully."}

    async def get_all_users(self, limit: int = 100, offset: int = 0) -> list[UserOutputDTO]:
        cached = await redis_client.get("admin:users")
        if cached:
            return _users_adapter.validate_json(cached)
        users = await self.repo.get_all(limit, offset)
        if not users:
            raise UsersNotFoundError()
        output = [UserOutputDTO.model_validate(u) for u in users]
        await redis_client.set("admin:users", _users_adapter.dump_json(output), ex=60)
        return output

    async def get_verified_active(self, limit: int = 100, offset: int = 0) -> list[UserOutputDTO]:
        users = await self.repo.get_verified_active(limit, offset)
        if not users:
            raise UsersNotFoundError()
        return [UserOutputDTO.model_validate(u) for u in users]

    async def save_payment_id(self, user_id: int, payment_id: str) -> dict:
        user = await self.repo.set_payment_id(user_id, payment_id)
        if not user:
            raise UserNotFoundError(user_id)
        return {"message": "Payment method saved."}
