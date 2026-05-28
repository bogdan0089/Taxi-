from pydantic import BaseModel


class TripCreateDTO(BaseModel):
    pickup_address: str
    dropoff_address: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float


class CreateRatingDTO(BaseModel):
    driver_id: int
    score: int
