import uuid
from typing import Annotated

from redis.asyncio import Redis
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKey
from app.dependencies import get_session, get_redis_client
from app.orm.models import Admin
from app.schemas import LoginSchema, TokenReadSchema
from app.settings import app_config
from app.utils import generate_password_hash

__all__ = ('auth_router',)

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/login', response_model=TokenReadSchema)
async def login(
        data: Annotated[LoginSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)],
        cache: Annotated[Redis, Depends(get_redis_client)]
) -> TokenReadSchema:
    """Login user. Returns a Bearer token to use for authorization.

    :param data: User credentials.
    :type data: LoginSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :param cache: Redis client instance.
    :type cache: Redis
    :return: Bearer token.
    :rtype: dict[str, str]
    :raises HTTPException: If credentials are invalid (401)
    """
    admin = await session.scalar(
        select(Admin).filter_by(username=data.username)
    )

    # Check the user exists and credentials are valid
    if not admin or admin.password != generate_password_hash(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials.'
        )

    # Generate a random token as a 36-char string
    token = str(uuid.uuid4())

    cache_key = CacheKey.access_token.format(token=token)

    # Save token in cache with a TTL of `app_config.server.access_token_ttl`
    #  seconds.
    await cache.set(
        cache_key,
        admin.id,  # type: ignore
        ex=app_config.server.access_token_ttl
    )

    return TokenReadSchema(access_token=token, token_type='bearer')
