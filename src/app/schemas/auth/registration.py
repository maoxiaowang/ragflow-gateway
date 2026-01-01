from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from app.core.validators.password import validate_complexity


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    password1: str = Field(..., min_length=6)
    password2: str = Field(..., min_length=6)
    invite_code: str = Field(..., min_length=8)

    @field_validator("password1")
    def validate_password1(cls, v):  # noqa
        return validate_complexity(v)

    @field_validator("password2")
    def passwords_match(cls, v, info):  # noqa
        validate_complexity(v)
        password1 = info.data.get("password1")
        if password1 is not None and v != password1:
            raise PydanticCustomError(
                "password_mismatch",
                "Passwords do not match"
            )
        return v
