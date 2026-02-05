from redis.asyncio import Redis

from settings import settings

redis_client: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


async def get_redis() -> Redis:
    return redis_client


async def close_redis() -> None:
    await redis_client.aclose()
