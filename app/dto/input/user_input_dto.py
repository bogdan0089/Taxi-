from pydantic import BaseModel, EmailStr, field_validator
from app.enums.role_enum import Role


class RegisterUserDTO(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Role = Role.PASSENGER

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class UpdateUserDTO(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None


class LoginUserDTO(BaseModel):
    email: EmailStr
    password: str
