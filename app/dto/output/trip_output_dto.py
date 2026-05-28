from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.enums.status_enum import Status


class TripOutputDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    passenger_id: int
    driver_id: int | None
    status: Status
    pickup_address: str
    dropoff_address: str
    price: float
    created_at: datetime
