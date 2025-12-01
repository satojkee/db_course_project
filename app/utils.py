import hashlib

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import app_config
from app.orm.models import Base

__all__ = ('pk_exists', 'generate_password_hash',)


async def pk_exists(
        session: AsyncSession,
        model: type[Base],
        primary_key: int
) -> None:
    """Checks if a primary key exists in the database for a given model.

    If the primary key does not exist, raises an HTTPException to signal that
    the provided information is invalid.

    :param session: Asynchronous SQLAlchemy session.
    :type session: AsyncSession
    :param model: The ORM model to check for the existence of the primary key.
    :type model: type[Base]
    :param primary_key: Primary key to check for existence.
    :type primary_key: int
    :return: None
    :raises HTTPException: If the primary key does not exist for the model.
    """
    instance = await session.get(model, primary_key)

    if instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid information supplied.'
        )


def generate_password_hash(password: str) -> str:
    """Generates a password hash using SHA-256.

    :param password: Password to hash.
    :type password: str
    :return: Hashed password.
    :rtype: str
    """
    return hashlib.sha256(
        f'{app_config.server.secret_key}{password}'.encode('utf-8')
    ).hexdigest()
