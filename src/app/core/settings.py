import os
from enum import Enum
from typing import Optional, Any
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "development").lower()

__all__ = [
    "Env",
    "settings"
]


def Env(env_name: str, default: Any=...) -> Any:
    field_default = default if default is not None else ...
    return Field(field_default, env=env_name)  # type: ignore


class PasswordComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BaseConfig(BaseSettings):
    env: str = Field('development', env="ENV")  # type: ignore
    log_dir: str = Env("LOG_DIR", "")

    # -------- Security --------
    secret_key: str = Env("SECRET_KEY")
    debug: bool = Env("DEBUG", False)
    access_token_expire_minutes: int =  Env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = Env("REFRESH_TOKEN_EXPIRE_DAYS", 7)

    login_url: str = Env("LOGIN_URL", "/api/v1/auth/login")
    password_complexity: PasswordComplexity = Env("PASSWORD_COMPLEXITY", "MEDIUM")

    # -------- Postgres --------
    db_host: str = Env("DB_HOST")
    db_port: int = Env("DB_PORT")
    db_user: str = Env("DB_USER")
    db_password: str = Env("DB_PASSWORD")
    db_name: str = Env("DB_NAME")
    database_url: Optional[str] = None

    # -------- Redis --------
    redis_host: str = Env("REDIS_HOST")
    redis_port: int = Env("REDIS_PORT")
    redis_password: Optional[str] = Env("REDIS_PASSWORD", None)
    redis_default_db: int = Env("REDIS_DEFAULT_DB", 0)
    redis_task_db: int = Env("REDIS_TASK_DB", 1)

    redis_default_url: Optional[str] = None
    redis_task_url: Optional[str] = None

    # -------- RAGFlow ---------
    ragflow_base_url: str = Env("RAGFLOW_BASE_URL")
    ragflow_api_key: str = Env("RAGFLOW_API_KEY")
    ragflow_timeout_seconds: int = Env("RAGFLOW_TIMEOUT_SECONDS", 30)

    class Config:
        env_file = ".env" if ENV == "development" else None
        env_file_encoding = "utf-8"

    @classmethod
    def _construct_redis_url(cls, v, info, db_key):
        if v is not None:
            return v
        values = info.data
        pwd = values.get("redis_password")
        host = values.get("redis_host")
        port = values.get("redis_port")
        db = values.get(db_key)

        if pwd:
            return f"redis://:{pwd}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @field_validator("redis_default_url", mode="before")
    @classmethod
    def build_default_redis_url(cls, v, info):
        return cls._construct_redis_url(v, info, db_key="redis_default_db")

    @field_validator("redis_task_url", mode="before")
    @classmethod
    def build_task_redis_url(cls, v, info):
        return cls._construct_redis_url(v, info, db_key="redis_task_db")

    @field_validator("database_url", mode="before")
    @classmethod
    def build_database_url(cls, v, info):
        if v is not None:
            return str(v)
        values = info.data
        user = quote_plus(values['db_user'])
        password = quote_plus(values['db_password'])
        host = values['db_host']
        port = values['db_port']
        dbname = values['db_name']
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


class DevelopmentConfig(BaseConfig):
    debug: bool = True
    access_token_expire_minutes: int = Env("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30)
    refresh_token_expire_days: int = Env("REFRESH_TOKEN_EXPIRE_DAYS", 90)


class TestingConfig(BaseConfig):
    debug: bool = False


class StagingConfig(BaseConfig):
    debug: bool = False


class ProductionConfig(BaseConfig):
    debug: bool = False


# 根据 ENV 选择配置
if ENV == "production":
    settings = ProductionConfig()  # type: ignore
elif ENV == "testing":
    settings = TestingConfig()  # type: ignore
elif ENV == "staging":
    settings = StagingConfig()  # type: ignore
else:
    settings = DevelopmentConfig()  # type: ignore
