from pydantic import BaseModel


class TokenOutputDTO(BaseModel):
    access_token: str
    refresh_token: str
