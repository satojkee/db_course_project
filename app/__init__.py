from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.orm import create_tables
from app.routers import (
    category_router,
    rate_router,
    city_router,
    country_router,
    customer_router,
    phone_router,
    call_router,
    payment_router, auth_router
)

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

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(rate_router)
app.include_router(city_router)
app.include_router(country_router)
app.include_router(customer_router)
app.include_router(phone_router)
app.include_router(call_router)
app.include_router(payment_router)
