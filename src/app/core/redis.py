from fastapi import Request
from redis.asyncio import Redis

from app.core.settings import settings


async def get_redis(request: Request) -> Redis:
    """
    用于接口请求的依赖注入
    """
    return request.app.state.redis


async def get_task_redis() -> Redis:
    """
    用于 TaskIQ 任务或非 HTTP 上下文，多进程安全
    """
    redis = Redis.from_url(
        str(settings.redis_task_url),
        encoding="utf-8",
        decode_responses=True,
    )
    return redis
