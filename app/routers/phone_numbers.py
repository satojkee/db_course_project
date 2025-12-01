from typing import Annotated

from fastcrud import FastCRUD
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import app_config
from app.dependencies import get_session, check_auth_token
from app.schemas import PhoneReadSchema, PhoneCreateSchema
from app.utils import pk_exists
from app.orm.models import PhoneNumber, Customer

__all__ = ('phone_router',)


phone_router = APIRouter(prefix='/phone_numbers', tags=['Phone Numbers'])

# Automatic crud operations for the ``PhoneNumber`` model
phone_repo = FastCRUD(PhoneNumber)


@phone_router.post(
    '',
    response_model=PhoneReadSchema | None,
    dependencies=[Depends(check_auth_token)]
)
async def create_phone_number(
        data: Annotated[PhoneCreateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> PhoneReadSchema | None:
    """Create a new number.

    :param data: Phone number data.
    :type data: PhoneCreateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Created phone number.
    :rtype: PhoneReadSchema
    :raises HTTPException:
        If a customer with such ID does not exist (404).
        If a customer already has 3 phone numbers (403).
        If a phone number already exists (409).
    """
    await pk_exists(session, Customer, data.customer_id)

    ph_numbers_count = await session.scalar(
        select(func.count())
        .select_from(PhoneNumber)
        .filter_by(customer_id=data.customer_id)
    )

    # Check if the customer has reached the limit
    if ph_numbers_count >= app_config.misc.max_phone_numbers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Customer has reached the limit of phone numbers.'
        )

    try:
        return await phone_repo.create(
            session,
            object=data,
            schema_to_select=PhoneReadSchema,
            return_as_model=True
        )
    except IntegrityError as e:
        if 'phone_numbers_number_key' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Phone number already exists.'
            )
        raise


@phone_router.get(
    '',
    response_model=dict[str, list[PhoneReadSchema] | int],
    dependencies=[Depends(check_auth_token)]
)
async def get_phone_numbers(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, list[PhoneReadSchema] | int]:
    """Returns all phone numbers present in the database.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: All phone numbers and their count.
    :rtype: dict[str, list[PhoneReadSchema] | int]
    """
    return await phone_repo.get_multi(
        session,
        limit=None,
        return_as_model=True,
        schema_to_select=PhoneReadSchema
    )


@phone_router.get(
    '/{phone_id:int}',
    response_model=PhoneReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def get_phone_number(
        phone_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> PhoneReadSchema:
    """Returns a phone number with a given ID.

    :param phone_id: ID of the phone number to return.
    :type phone_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Phone number with the given ID.
    :rtype: PhoneReadSchema
    :raises HTTPException: If phone number with such ID does not exist (404).
    """
    phone = await phone_repo.get(
        session,
        id=phone_id,
        schema_to_select=PhoneReadSchema,
        return_as_model=True
    )

    if phone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such phone number.'
        )

    return phone


@phone_router.delete(
    '/{phone_id:int}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_auth_token)]
)
async def delete_phone_number(
        phone_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Deletes an existing phone number from the database.

    :param phone_id: ID of the phone number to delete.
    :type phone_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: None
    :raises HTTPException: If phone number with such ID does not exist (404).
    """
    try:
        await phone_repo.delete(
            session,
            id=phone_id,
            allow_multiple=False
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such phone number.'
        )
