import re
from typing import Optional

from pydantic import BaseModel, field_validator, Field
from pydantic_core import PydanticCustomError


class UserLogin(BaseModel):
    username: str
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., min_length=20, max_length=512)

    @field_validator("refresh_token")
    def validate_format(cls, v: str):  # noqa
        if not re.fullmatch(r"[A-Za-z0-9._~-]+", v):
            raise PydanticCustomError(
                "invalid_token_format",
                "Invalid token format of refresh token."
            )
        return str(v)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
