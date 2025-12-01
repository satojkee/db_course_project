from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastcrud import FastCRUD
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session, check_auth_token
from app.utils import pk_exists
from app.schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryReadSchema
)
from app.orm.models import Category, Rate

__all__ = ('category_router',)

category_router = APIRouter(prefix='/categories', tags=['Categories'])

# Automatic crud operations for the ``Category`` model
category_repo = FastCRUD(Category)


@category_router.post(
    '',
    response_model=CategoryReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def create_category(
        data: Annotated[CategoryCreateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CategoryReadSchema:
    """Creates a new category in the database.

    :param data: Category creation data.
    :type data: CategoryCreateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Created category.
    :raises HTTPException: If rate with such ID does not exist (404).
    """
    await pk_exists(session, Rate, data.rate_id)

    return await category_repo.create(
        session,
        object=data,
        schema_to_select=CategoryReadSchema,
        return_as_model=True
    )


@category_router.get(
    '',
    response_model=dict[str, list[CategoryReadSchema] | int],
    dependencies=[Depends(check_auth_token)]
)
async def get_categories(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, list[CategoryReadSchema] | int]:
    """Returns all categories present in the database.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: All categories and their count.
    :rtype: dict[str, list[CategoryReadSchema] | int]
    """
    return await category_repo.get_multi(
        session,
        limit=None,
        return_as_model=True,
        schema_to_select=CategoryReadSchema
    )


@category_router.get(
    '/{category_id:int}',
    response_model=CategoryReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def get_category(
        category_id: int,
        session: Annotated[AsyncSession, Depends(get_session)],
) -> CategoryReadSchema:
    """Returns a category with a given ID.

    :param category_id: ID of the category to return.
    :type category_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Category with the given ID.
    :raises HTTPException: If category with such ID does not exist (404).
    """
    category = await category_repo.get(
        session,
        id=category_id,
        schema_to_select=CategoryReadSchema,
        return_as_model=True
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such category.'
        )

    return category


@category_router.patch(
    '/{category_id:int}',
    dependencies=[Depends(check_auth_token)]
)
async def update_category(
        category_id: int,
        data: Annotated[CategoryUpdateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Updates an existing category in the database.

    :param category_id: ID of the category to update.
    :type category_id: int
    :param data: Category update data.
    :type data: CategoryUpdateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: None
    :raises HTTPException: If rate with such ID does not exist (404).
    """
    if data.rate_id is not None:
        await pk_exists(session, Rate, data.rate_id)

    try:
        await category_repo.update(
            session,
            id=category_id,
            object=data,
            allow_multiple=False,
            return_as_model=True,
            schema_to_select=CategoryReadSchema
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such category.'
        )


@category_router.delete(
    '/{category_id:int}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_auth_token)]
)
async def delete_category(
        category_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Deletes an existing category from the database.

    :param category_id: ID of the category to delete.
    :type category_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: None
    :raises HTTPException: If category with such ID does not exist (404).
    """
    try:
        await category_repo.delete(
            session,
            id=category_id,
            allow_multiple=False
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such category.'
        )
