import os
from enum import Enum
from typing import Optional
from urllib.parse import quote_plus

from pydantic import Field, model_validator, BaseModel, PostgresDsn, RedisDsn, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import DEFAULT_CONFIG_DIR, DEFAULT_UPLOAD_DIR, DEFAULT_LOG_DIR
from app.core.paths import ROOT_DIR

__all__ = [
    "settings"
]


class EnvEnum(str, Enum):
    prod = "PROD"
    test = "TEST"
    dev = "DEV"


ENV = os.getenv("ENV", EnvEnum.dev.value).upper()


class PasswordComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DBConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5432
    user: str = "root"
    password: str
    name: str = "ragflow_gateway"
    dsn: Optional[PostgresDsn] = None
    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 6379
    password: str
    default_db: int = 0
    task_db: int = 1
    default_dsn: Optional[RedisDsn] = None
    task_dsn: Optional[RedisDsn] = None
    model_config = SettingsConfigDict(env_prefix="REDIS_")


class RAGFlowConfig(BaseSettings):
    origin_url: str
    api_key: str
    api_version: str = "v1"
    timeout_seconds: int = 10

    model_config = SettingsConfigDict(env_prefix="RAG_")


class BaseConfig(BaseSettings):
    # 基础配置
    env: str = Field(EnvEnum.dev.value)
    log_dir: str = Field(DEFAULT_LOG_DIR)
    upload_dir: str = Field(DEFAULT_UPLOAD_DIR)
    config_dir: str = Field(DEFAULT_CONFIG_DIR)
    login_url: Optional[str] = Field("/api/v1/auth/login")

    # 安全配置
    secret_key: str = Field(...)
    debug: Optional[bool] = Field(False)
    access_token_expire_minutes: Optional[int] = Field(30)
    refresh_token_expire_days: Optional[int] = Field(7)
    password_complexity: Optional[str] = Field("HIGH")
    cors_origins: Optional[list[AnyUrl]] = Field(list())

    # 模块配置
    redis: RedisConfig
    db: DBConfig
    ragflow: RAGFlowConfig

    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_nested_max_split=1,
        env_file=ROOT_DIR / ".env" if ENV == EnvEnum.dev.value else None,
        env_file_encoding="utf-8"
    )

    def _construct_redis_url(self, db):
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{db}"
        return f"redis://{self.redis.host}:{self.redis.port}/{db}"

    @model_validator(mode="after")
    def build_urls(self):
        if not self.db.dsn:
            user = quote_plus(self.db.user)
            password = quote_plus(self.db.password)
            self.db.dsn = PostgresDsn(
                f"postgresql+asyncpg://{user}:{password}"
                f"@{self.db.host}:{self.db.port}/{self.db.name}"
            )

        if not self.redis.default_dsn:
            self.redis.default_dsn = RedisDsn(self._construct_redis_url(self.redis.default_db))

        if not self.redis.task_dsn:
            self.redis.task_dsn = RedisDsn(self._construct_redis_url(self.redis.task_db))
        return self

    @model_validator(mode="before")
    def parse_cors_origins(self):
        cors_origins = self.get("cors_origins")
        self["cors_origins"] = [item.strip().rstrip("/") for item in cors_origins.split(",")]
        return self


class DevelopmentConfig(BaseConfig):
    debug: bool = True
    access_token_expire_minutes: int = Field(60 * 24 * 30)
    refresh_token_expire_days: int = Field(90)


class TestingConfig(BaseConfig):
    debug: bool = False


class StagingConfig(BaseConfig):
    debug: bool = False


class ProductionConfig(BaseConfig):
    debug: bool = False


# 根据 ENV 选择配置
_config_map = {
    EnvEnum.prod.value: ProductionConfig,
    EnvEnum.test.value: TestingConfig,
    EnvEnum.dev.value: DevelopmentConfig,
}
settings = _config_map.get(ENV, DevelopmentConfig)()  # type: ignore
