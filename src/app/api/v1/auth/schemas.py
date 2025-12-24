import re
from datetime import datetime
from functools import partial
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_core import PydanticCustomError

from app.core.settings import settings

COMPLEXITY_RULES = {
    "LOW": {
        "uppercase": False,
        "lowercase": False,
        "digits": False,
        "symbols": False,
        "min_length": 6
    },
    "MEDIUM": {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "symbols": False,
        "min_length": 6
    },
    "HIGH": {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "symbols": True,
        "min_length": 8
    }
}

PasswordError = partial(PydanticCustomError, "password_complexity")
SYMBOLS = r"!@#$%^&*()_+-=[]{}|;:'\",.<>?/"


def validate_complexity(v: str) -> str:
    rules = COMPLEXITY_RULES[settings.password_complexity]
    errors = list()
    if len(v) < rules["min_length"]:
        errors.append(f"Password must be at least {rules["min_length"]} characters long")
    if rules["uppercase"] and not re.search(r"[A-Z]", v):
        errors.append("Password must contain at least one uppercase letter")
    if rules["lowercase"] and not re.search(r"[a-z]", v):
        errors.append("Password must contain at least one lowercase letter")
    if rules["digits"] and not re.search(r"[0-9]", v):
        errors.append("Password must contain at least one digit")
    if rules["symbols"] and not re.search(rf"[{re.escape(SYMBOLS)}]", v):
        errors.append("Password must contain at least one symbol")
    if errors:
        raise PasswordError(", ".join(errors))
    return v


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_complexity(v)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    password1: str = Field(..., min_length=6)
    password2: str = Field(..., min_length=6)

    @field_validator('password1')
    @classmethod
    def validate_password1(cls, v):
        return validate_complexity(v)

    @field_validator('password2')
    @classmethod
    def passwords_match(cls, v, info):
        validate_complexity(v)
        password1 = info.data.get('password1')
        if password1 is not None and v != password1:
            raise PydanticCustomError(
                'password_mismatch',
                'Passwords do not match'
            )
        return v


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    is_active: bool
    avatar: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenOut(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str = Field(..., min_length=20, max_length=512)

    @field_validator('refresh_token')
    @classmethod
    def validate_format(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9._~-]+", v):
            raise PydanticCustomError(
                'invalid_token_format',
                'Invalid token format of refresh token.'
            )
        return v
