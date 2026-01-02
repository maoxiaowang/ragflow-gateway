from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.core.validators.password import validate_complexity
from app.schemas.iam.role import RoleOut


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

    @field_validator("password")
    def validate_password(cls, v: str) -> str:  # noqa
        return validate_complexity(v)


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    is_active: bool
    avatar: str | None = None
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserCheckPermOut(BaseModel):
    id: int
    is_active: bool
    is_superuser: bool
    roles: List[RoleOut] = []

    model_config = ConfigDict(
        from_attributes=True
    )
