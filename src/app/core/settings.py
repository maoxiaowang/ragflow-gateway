import os
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

__all__ = [
    "settings"
]


class EnvEnum(str, Enum):
    prod = "PROD"
    test = "TEST"
    dev = "DEV"


BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
ENV = os.getenv("ENV", EnvEnum.dev.value).upper()


def Env(env_name: str, default: Any = ...) -> Any:
    field_default = default if default is not None else ...
    return Field(field_default, env=env_name)  # type: ignore


class PasswordComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BaseConfig(BaseSettings):
    env: str = Env("ENV", EnvEnum.dev.value)  # type: ignore
    log_dir: str = Env("LOG_DIR", "")
    upload_dir: str = Env("UPLOAD_DIR", "")

    # -------- Security --------
    secret_key: str = Env("SECRET_KEY")
    debug: bool = Env("DEBUG", False)
    access_token_expire_minutes: int = Env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = Env("REFRESH_TOKEN_EXPIRE_DAYS", 7)

    login_url: str = Env("LOGIN_URL", "/api/v1/auth/login")
    password_complexity: PasswordComplexity = Env("PASSWORD_COMPLEXITY", "HIGH")

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
        env_file = str(BASE_DIR.parent.parent / ".env") if ENV == EnvEnum.dev.value else None
        env_file_encoding = "utf-8"

    def _construct_redis_url(self, db):
        pwd = self.redis_password
        host = self.redis_host
        port = self.redis_port

        if pwd:
            return f"redis://:{pwd}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @model_validator(mode="after")
    def build_urls(self):
        # ---------- Database URL ----------
        if not self.database_url:
            user = quote_plus(self.db_user)
            password = quote_plus(self.db_password)
            host = self.db_host
            port = self.db_port
            dbname = self.db_name
            self.database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"

        # ---------- Redis URL ----------
        if not self.redis_default_url:
            self.redis_default_url = self._construct_redis_url(self.redis_default_db)

        if not self.redis_task_url:
            self.redis_task_url = self._construct_redis_url(self.redis_task_db)

        return self


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
_config_map = {
    EnvEnum.prod.value: ProductionConfig,
    EnvEnum.test.value: TestingConfig,
    EnvEnum.dev.value: DevelopmentConfig,
}
settings = _config_map.get(ENV, DevelopmentConfig)()
