import os
from typing import Optional
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "development").lower()


class BaseConfig(BaseSettings):
    env: str = Field('development', env="ENV")  # type: ignore
    log_dir: str = Field('', env="LOG_DIR")

    # -------- Security --------
    secret_key: str = Field(..., env="SECRET_KEY")
    debug: bool = Field(False, env="DEBUG")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    login_url: str = Field('/api/v1/auth/login', env="LOGIN_URL")

    # -------- Postgres --------
    db_host: str = Field(..., env="DB_HOST")
    db_port: int = Field(..., env="DB_PORT")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_name: str = Field(..., env="DB_NAME")
    database_url: str = None

    # -------- Redis --------
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_default_db: int = Field(0, env="REDIS_DEFAULT_DB")
    redis_task_db: int = Field(1, env="REDIS_TASK_DB")

    redis_default_url: str = None
    redis_task_url: str = None

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
        print(values)
        user = quote_plus(values['db_user'])
        password = quote_plus(values['db_password'])
        host = values['db_host']
        port = values['db_port']
        dbname = values['db_name']
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


class DevelopmentConfig(BaseConfig):
    debug: bool = True
    access_token_expire_minutes: int = Field(60 * 24 * 30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(90, env="REFRESH_TOKEN_EXPIRE_DAYS")


class TestingConfig(BaseConfig):
    debug: bool = False


class StagingConfig(BaseConfig):
    debug: bool = False


class ProductionConfig(BaseConfig):
    debug: bool = False


# 根据 ENV 选择配置
if ENV == "production":
    settings = ProductionConfig()
elif ENV == "testing":
    settings = TestingConfig()
elif ENV == "staging":
    settings = StagingConfig()
else:
    settings = DevelopmentConfig()
