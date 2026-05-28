from pydantic import BaseModel, ConfigDict


class RatingOutputDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    passenger_id: int
    driver_id: int
    score: int
