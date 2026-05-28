from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.core.exceptions import TokenInvalidError, TokenExpiredError, UserNotFoundError
from app.core.redis import redis_client
import jwt


class AuthService:

    @staticmethod
    def decode_token(token: str) -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise UserNotFoundError()
            return int(user_id)
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()


    @staticmethod
    def create_access_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    @staticmethod
    async def create_refresh_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
        await redis_client.set(f"refresh:{user_id}", token, ex=60 * 60 * 24 * 7)
        return token

    @staticmethod
    async def refresh_access_token(token: str) -> str:
        user_id = AuthService.decode_token(token)
        stored = await redis_client.get(f"refresh:{user_id}")
        if not stored:
            raise TokenInvalidError()
        return AuthService.create_access_token(user_id)

    @staticmethod
    async def logout(user_id: int) -> dict:
        await redis_client.delete(f"refresh:{user_id}")
        return {"message": "Logged out successfully."}
