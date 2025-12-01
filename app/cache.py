from dataclasses import dataclass

from redis.asyncio import Redis

from app.settings import app_config

__all__ = ('redis_client', 'CacheKey')

redis_client = Redis.from_url(
    url=app_config.redis.uri.__str__(),
    max_connections=app_config.redis.max_connections,
    decode_responses=app_config.redis.decode_responses,
    socket_timeout=app_config.redis.socket_timeout,
    single_connection_client=app_config.redis.single_connection_client
)


@dataclass(frozen=True)
class CacheKey:
    access_token: str = 'access_token:{token}'
