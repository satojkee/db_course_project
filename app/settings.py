import sys

from loguru import logger
from pydantic import PostgresDsn, ValidationError, BaseModel, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ('app_config',)


class Postgres(BaseModel):
    """Contains postgres settings."""

    uri: PostgresDsn
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 5
    pool_recycle: int = 1800
    max_overflow: int = 5


class Redis(BaseModel):
    """Contains redis settings."""

    uri: RedisDsn
    max_connections: int = 10
    socket_timeout: int = 10
    decode_responses: bool = True
    single_connection_client: bool = False


class Misc(BaseModel):
    """Contains miscellaneous settings."""

    max_phone_numbers: int = 3


class Server(BaseModel):
    """Contains server settings."""

    secret_key: str
    access_token_ttl: int = 24 * 60 * 60


class AppConfig(BaseSettings):
    """Responsible for loading and validation of application settings.
    """

    postgres: Postgres
    redis: Redis
    misc: Misc
    server: Server

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='__'
    )


try:
    # noinspection PyArgumentList
    app_config = AppConfig()
except ValidationError as e:
    logger.error(f'Validation error during config initialization: {e}')

    sys.exit(-1)
