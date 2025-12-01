from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastcrud import FastCRUD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from app.dependencies import get_session, check_auth_token
from app.utils import pk_exists
from app.schemas import (
    CityCreateSchema,
    CityUpdateSchema,
    CityReadSchema,
    TopCitySchema
)
from app.orm.models import City, Country, Customer, Call

__all__ = ('city_router',)

city_router = APIRouter(prefix='/cities', tags=['Cities'])

# Automatic crud operations for the ``City`` model
city_repo = FastCRUD(City)


@city_router.post(
    '',
    response_model=CityReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def create_city(
        data: Annotated[CityCreateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CityReadSchema:
    """Creates a new city in the database.

    :param data: City creation data.
    :type data: CityCreateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Created city.
    :rtype: CityReadSchema
    :raises HTTPException: If country with such ID does not exist (404).
    """
    await pk_exists(session, Country, data.country_id)

    return await city_repo.create(
        session,
        object=data,
        schema_to_select=CityReadSchema,
        return_as_model=True
    )


@city_router.get(
    '',
    response_model=dict[str, list[CityReadSchema] | int],
    dependencies=[Depends(check_auth_token)]
)
async def get_cities(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, list[CityReadSchema] | int]:
    """Returns all cities present in the database.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: All cities and their count.
    :rtype: dict[str, list[CityReadSchema] | int]
    """
    return await city_repo.get_multi(
        session,
        limit=None,
        return_as_model=True,
        schema_to_select=CityReadSchema
    )


@city_router.get(
    '/{city_id:int}',
    response_model=CityReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def get_city(
        city_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CityReadSchema:
    """Returns a city with a given ID.

    :param city_id: ID of the city to return.
    :type city_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: City with the given ID.
    :raises HTTPException: If city with such ID does not exist (404).
    """
    city = await city_repo.get(
        session,
        id=city_id,
        schema_to_select=CityReadSchema,
        return_as_model=True
    )

    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such city.'
        )

    return city


@city_router.patch(
    '/{city_id:int}',
    dependencies=[Depends(check_auth_token)]
)
async def update_city(
        city_id: int,
        data: Annotated[CityUpdateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Updates an existing city in the database.

    :param city_id: ID of the city to update.
    :type city_id: int
    :param data: City update data.
    :type data: CityUpdateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: None
    """
    try:
        await city_repo.update(
            session,
            id=city_id,
            object=data,
            allow_multiple=False,
            return_as_model=True,
            schema_to_select=CityReadSchema,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such city.'
        )


@city_router.delete(
    '/{city_id:int}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_auth_token)]
)
async def delete_city(
        city_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Deletes an existing city from the database.

    :param city_id: ID of the city to delete.
    :type city_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    """
    try:
        await city_repo.delete(
            session,
            id=city_id,
            allow_multiple=False,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such city.'
        )


@city_router.get(
    '/top',
    response_model=TopCitySchema | None,
    dependencies=[Depends(check_auth_token)]
)
async def get_top_city(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> TopCitySchema | None:
    """Returns the city with the highest number of internal calls.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Most popular city.
    :rtype: dict[str, int | CityUpdateSchema]
    """
    CallFrom = aliased(Customer)  # noqa pylint: N806
    CallTo = aliased(Customer)  # noqa pylint: N806

    top_city = await session.execute(
        select(City, func.count().label('total_calls'))
        .join(CallFrom, City.id == CallFrom.city_id)
        .join(Call, Call.from_customer_id == CallFrom.id)
        .join(CallTo, Call.to_customer_id == CallTo.id)
        .group_by(City.id)
        .order_by(func.count().desc())
        .limit(1)
    )

    if top_city is not None:
        city, internal_calls = top_city.first()
        return TopCitySchema(
            internal_calls=internal_calls,
            city=CityReadSchema.model_validate(city)
        )

    return None
