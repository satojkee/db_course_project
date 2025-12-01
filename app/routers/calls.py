"""Endpoints in this module are designed for testing purposes only.
These endpoints are not intended to be used in any "production" versions.
The only purpose is to demonstrate and test database triggers behavior.

Authorization is not required for these endpoints.
"""

from typing import Annotated

from fastcrud import FastCRUD
from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import func, select, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.types import CallStatus
from app.dependencies import get_session
from app.schemas import CallCreateSchema, CallReadSchema, CallUpdateSchema
from app.orm.models import Call, PhoneNumber

__all__ = ('call_router',)

call_router = APIRouter(prefix='/calls', tags=['Calls'])

# Automatic crud operations for the ``Call`` model
call_repo = FastCRUD(Call)


@call_router.post('/start', response_model=CallReadSchema)
async def start_call(
        data: Annotated[CallCreateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CallReadSchema:
    """Starts a calls.

    :param data: Call creation data.
    :type data: CallCreateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Created call.
    :rtype: CallReadSchema
    :raises HTTPException: If customer with such ID does not exist (404).
    """
    if data.from_customer_id == data.to_customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cannot make a call with the same customer.'
        )

    active_call_count = await session.scalar(
        select(func.count())
        .select_from(Call)
        .where(
            or_(
                Call.from_customer_id.in_(
                    [data.from_customer_id, data.to_customer_id]
                ),
                Call.to_customer_id.in_(
                    [data.from_customer_id, data.to_customer_id]
                )
            ),
            Call.status == CallStatus.IN_PROGRESS
        )
    )

    # Check if either customer is already in an active call
    if active_call_count > 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='One of the customers is already in an active call.'
        )

    # Check if both have at least one registered phone number
    for customer_id, role in [(data.from_customer_id, 'from_customer'),
                              (data.to_customer_id, 'to_customer')]:
        count = await session.scalar(
            select(func.count())
            .select_from(PhoneNumber)
            .where(PhoneNumber.customer_id == customer_id)
        )
        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{role} must have at least one phone number.'
            )

    return await call_repo.create(
        session,
        object=data,
        return_as_model=True,
        schema_to_select=CallReadSchema
    )


@call_router.post('/finish/{call_id:int}', response_model=CallReadSchema)
async def finish_call(
        call_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CallReadSchema:
    """Finishes a call with a given ID.

    :param call_id: ID of the call to finish.
    :type call_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Finished call.
    :rtype: CallReadSchema
    :raises HTTPException: If call with such ID does not exist (404).
    """
    try:
        return await call_repo.update(
            session,
            id=call_id,
            status=CallStatus.IN_PROGRESS,
            object=CallUpdateSchema(status=CallStatus.FINISHED),
            schema_to_select=CallReadSchema,
            return_as_model=True
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such call or call is already finished.'
        )


@call_router.get('/{call_id:int}', response_model=CallReadSchema)
async def get_call(
        call_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CallReadSchema:
    """Returns a call with a given ID.

    :param call_id: ID of the call to return.
    :type call_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Call with the given ID.
    :rtype: CallReadSchema
    :raises HTTPException: If call with such ID does not exist (404).
    """
    call = await call_repo.get(
        session,
        id=call_id,
        schema_to_select=CallReadSchema,
        return_as_model=True
    )

    if call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such call.'
        )

    return call
