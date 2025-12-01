from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from app.settings import app_config


__all__ = (
    'AsyncSessionFactory',
    'async_engine',
    'create_tables'
)

async_engine = create_async_engine(
    url=str(app_config.postgres.uri),
    echo=app_config.postgres.echo,
    pool_pre_ping=app_config.postgres.pool_pre_ping,
    pool_size=app_config.postgres.pool_size,
    pool_recycle=app_config.postgres.pool_recycle,
    max_overflow=app_config.postgres.max_overflow
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def create_tables() -> None:
    """Creates necessary database tables if those not exist.

    :return: None
    """
    from app.orm.models import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
