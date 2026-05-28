from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.enums.role_enum import Role


class UserOutputDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    avg_rating: float
    created_at: datetime
