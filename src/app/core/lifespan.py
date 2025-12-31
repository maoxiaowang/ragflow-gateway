import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.db import engine
from redis.asyncio import Redis

from app.core.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动逻辑（可选）
    redis = Redis.from_url(
        str(settings.redis.default_dsn),
        encoding="utf-8",
        decode_responses=True,
    )
    app.state.redis = redis
    logger.info("Redis client initialized")

    yield
    # 关闭逻辑
    await redis.close()
    logger.info("Redis client closed")
    await engine.dispose()
