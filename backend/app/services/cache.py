import json
from typing import Optional
from app.core.config import settings

try:
    from redis.asyncio import Redis
except ImportError:  # Local fallback when optional infra deps are not installed yet.
    Redis = None

redis_client: Optional[Redis] = None


def get_redis():
    global redis_client
    if Redis is None:
        raise RuntimeError("Redis package is not installed")
    if redis_client is None:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def cache_get(key: str) -> Optional[dict]:
    try:
        value = await get_redis().get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


async def cache_set(key: str, value: dict, seconds: int) -> None:
    try:
        await get_redis().setex(key, seconds, json.dumps(value))
    except Exception:
        return None
