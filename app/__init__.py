from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.orm import create_tables
from app.routers import v1_router

__all__ = ('app',)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """This function is responsible for creating tables on application startup.

    **Note:**
        - Statements before ``yield`` executes on startup.
        - Statements after ``yield`` executes on shutdown.

    :param _: FastAPI application.
    :type _: FastAPI
    :return: None
    """
    await create_tables()
    yield

app = FastAPI(
    title='API Documentation',
    redoc_url='/api/docs/redoc',
    docs_url='/api/docs/swagger',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(v1_router)
