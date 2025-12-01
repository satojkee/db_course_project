from typing import Annotated

from fastcrud import FastCRUD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session, check_auth_token
from app.orm.models import Payment
from app.schemas import PaymentReadSchema

__all__ = ('payment_router',)

payment_router = APIRouter(prefix='/payments', tags=['Payments'])

# Automatic crud operations for the ``Payment`` model
payment_repo = FastCRUD(Payment)


@payment_router.get(
    '',
    response_model=dict[str, list[PaymentReadSchema] | int],
    dependencies=[Depends(check_auth_token)]
)
async def get_payments(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, list[PaymentReadSchema] | int]:
    """Returns all payments present in the database.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: All payments and their count.
    :rtype: dict[str, list[PaymentReadSchema] | int]
    """
    return await payment_repo.get_multi(
        session,
        limit=None,
        return_as_model=True,
        schema_to_select=PaymentReadSchema
    )


@payment_router.get(
    '/{payment_id:int}',
    response_model=PaymentReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def get_payment(
        payment_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> PaymentReadSchema:
    """Returns a payment with a given ID.

    :param payment_id: Payment ID.
    :type payment_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Payment with the given ID.
    :rtype: PaymentReadSchema
    :raises HTTPException: If payment with such ID does not exist (404).
    """
    payment = await payment_repo.get(
        session,
        id=payment_id,
        schema_to_select=PaymentReadSchema,
        return_as_model=True
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such payment.'
        )

    return payment
