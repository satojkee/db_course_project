from typing import AsyncGenerator, Annotated

from redis.asyncio import Redis
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import redis_client, CacheKey
from app.orm import AsyncSessionFactory
from app.settings import app_config

__all__ = ('get_session', 'get_redis_client', 'check_auth_token',)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Simple FastAPI dependency to get session from `AsyncSessionFactory`.

    :return: Asynchronous SQLAlchemy session instance.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with AsyncSessionFactory() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Simple FastAPI dependency to get Redis client from Redis pool.

    :return: Redis client instance.
    :rtype: AsyncGenerator[Redis, None]
    """
    yield redis_client


async def check_auth_token(
        redis: Annotated[Redis, Depends(get_redis_client)],
        authorization: Annotated[
            str | None,
            Header(..., description='Authorization token')
        ] = None
) -> None:
    """Validates authorization token. Raises a ``fastapi.HTTPException``
    in case of invalid token.

    :param redis: Redis client instance.
    :type redis: Redis
    :param authorization: Authorization token.
        Valid format: `Bearer <token>` or `<token>`.
    :type authorization: str | None
    :return: None
    :raises HTTPException:
        401 status code (Unauthorized) if token is missing or expired.
    """

    def _raise_http_error() -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or missing authorization token.'
        )

    if not authorization:
        _raise_http_error()

    authorization = authorization.replace('Bearer ', '')

    # Cache key format: access_token:{token_value}
    cache_key = CacheKey.access_token.format(token=authorization)

    # Get user ID from cache, it's none if token is invalid or expired
    user_id = await redis.get(cache_key)

    if not user_id:
        _raise_http_error()

    # Reset token TTL after every successful request
    await redis.expire(cache_key, app_config.server.access_token_ttl)
