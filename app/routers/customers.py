import calendar
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastcrud import FastCRUD
from sqlalchemy import select, func, extract
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.dependencies import get_session, check_auth_token
from app.types import CallStatus
from app.utils import pk_exists
from app.schemas import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerReadSchema,
    CustomerCityPairSchema,
    CityReadSchema,
    AvgCallChargePerYearSchema,
    MonthlyCallSumSchema,
    InDebtCustomerSchema,
)
from app.orm.models import Customer, City, Category, Call, Payment

__all__ = ('customer_router',)


customer_router = APIRouter(prefix='/customers', tags=['Customers'])

# Automatic crud operations for the ``Customer`` model
customer_repo = FastCRUD(Customer)


@customer_router.post(
    '',
    response_model=CustomerReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def create_customer(
        data: Annotated[CustomerCreateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CustomerReadSchema:
    """Creates a new customer in the database.
    
    :param data: Customer creation data.
    :type data: CustomerCreateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Created customer.
    :rtype: CustomerReadSchema
    :raises HTTPException:
        If a city or category with such ID does not exist (404).
        If a customer with a such passport already exists (409).
    """
    await pk_exists(session, City, data.city_id)
    await pk_exists(session, Category, data.category_id)

    try:
        return await customer_repo.create(
            session,
            object=data,
            schema_to_select=CustomerReadSchema,
            return_as_model=True
        )
    except IntegrityError as e:
        if 'customers_passport_key' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Customer with such passport already exists.'
            )
        raise


@customer_router.get(
    '',
    response_model=dict[str, list[CustomerReadSchema] | int],
    dependencies=[Depends(check_auth_token)]
)
async def get_customers(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> dict[str, list[CustomerReadSchema] | int]:
    """Returns all customers present in the database.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: All customers and their count.
    :rtype: dict[str, list[CustomerReadSchema] | int]
    """
    return await customer_repo.get_multi(
        session,
        limit=None,
        return_as_model=True,
        schema_to_select=CustomerReadSchema
    )


@customer_router.get(
    '/{customer_id:int}',
    response_model=CustomerReadSchema,
    dependencies=[Depends(check_auth_token)]
)
async def get_customer(
        customer_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> CustomerReadSchema:
    """Returns a customer with a given ID.

    :param customer_id: ID of the customer to return.
    :type customer_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Customer with the given ID.
    :rtype: CustomerReadSchema
    :raises HTTPException: If customer with such ID does not exist (404).
    """
    customer = await customer_repo.get(
        session,
        id=customer_id,
        schema_to_select=CustomerReadSchema,
        return_as_model=True
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such customer.'
        )

    return customer


@customer_router.patch(
    '/{customer_id:int}',
    dependencies=[Depends(check_auth_token)]
)
async def update_customer(
        customer_id: int,
        data: Annotated[CustomerUpdateSchema, Body(...)],
        session: Annotated[AsyncSession, Depends(get_session)]
) -> None:
    """Updates an existing customer in the database.

    :param customer_id: ID of the customer to update.
    :type customer_id: int
    :param data: Customer update data.
    :type data: CustomerUpdateSchema
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: None
    :raises HTTPException: If customer with such ID does not exist (404).
    """
    if data.city_id is not None:
        await pk_exists(session, City, data.city_id)

    if data.category_id is not None:
        await pk_exists(session, Category, data.category_id)

    try:
        await customer_repo.update(
            session,
            id=customer_id,
            object=data,
            allow_multiple=False,
            return_as_model=True,
            schema_to_select=CustomerReadSchema,
        )
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such customer.'
        )


@customer_router.get(
    '/top_city',
    response_model=list[CustomerCityPairSchema],
    dependencies=[Depends(check_auth_token)]
)
async def get_city_stats(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> list[CustomerCityPairSchema]:
    """Returns a list of customers with their "favorite" cities.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: List of customers with their cities.
    :rtype: list[CustomerCityPairSchema]
    """
    Caller = aliased(Customer)  # noqa pylint: N806
    Receiver = aliased(Customer)  # noqa pylint: N806

    # Outgoing calls
    outgoing = (
        select(
            Call.from_customer_id.label('customer_id'),
            Receiver.city_id.label('city_id'),  # type: ignore
            func.count(Call.id).label('call_count')
        )
        .join(Receiver, Call.to_customer_id == Receiver.id)
        .group_by(
            Call.from_customer_id,
            Receiver.city_id  # type: ignore
        )
    )

    # Incoming calls
    incoming = (
        select(
            Call.to_customer_id.label('customer_id'),
            Caller.city_id.label('city_id'),  # type: ignore
            func.count(Call.id).label('call_count')
        )
        .join(Caller, Call.from_customer_id == Caller.id)
        .group_by(
            Call.to_customer_id,
            Caller.city_id  # type: ignore
        )
    )

    # Combine incoming and outgoing calls by customer ID and city ID
    calls_per_city = outgoing.union_all(incoming).subquery()

    # Get total calls per city per user
    ranked = select(
        calls_per_city.c.customer_id,
        calls_per_city.c.city_id,
        func.sum(calls_per_city.c.call_count).label('total_calls'),
        func.rank().over(
            partition_by=calls_per_city.c.customer_id,
            order_by=func.sum(calls_per_city.c.call_count).desc()
        ).label('rank')
    ).group_by(
        calls_per_city.c.customer_id,
        calls_per_city.c.city_id
    ).subquery()

    # Get results
    top_city_per_user = await session.execute(
        select(Customer, City, ranked.c.total_calls)
        .join(Customer, Customer.id == ranked.c.customer_id)
        .join(City, City.id == ranked.c.city_id)
        .filter(ranked.c.rank == 1)  # type: ignore
    )

    return [
        CustomerCityPairSchema(
            customer=CustomerReadSchema.model_validate(customer),
            city=CityReadSchema.model_validate(city),
            total_calls=total
        )
        for customer, city, total in top_city_per_user.all()
    ]


@customer_router.get(
    '/calls_with_all_cities',
    response_model=list[CustomerReadSchema],
    dependencies=[Depends(check_auth_token)]
)
async def get_customers_with_all_cities(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> list[CustomerReadSchema]:
    """Returns a list of customers who have called all cities.

    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: List of customers who have called all cities.
    :rtype: list[CustomerReadSchema]
    """
    Caller = aliased(Customer)  # noqa pylint: N806
    Receiver = aliased(Customer)  # noqa pylint: N806

    # Outgoing calls: customer_id + city_id
    outgoing = (
        select(
            Call.from_customer_id.label('customer_id'),
            Receiver.city_id.label('city_id')  # type: ignore
        )
        .join(Receiver, Call.to_customer_id == Receiver.id)
    )

    # Incoming calls: customer_id + city_id
    incoming = (
        select(
            Call.to_customer_id.label('customer_id'),
            Caller.city_id.label('city_id')  # type: ignore
        )
        .join(Caller, Call.from_customer_id == Caller.id)
    )

    # Combine incoming and outgoing calls by customer ID and city ID
    calls_per_city = outgoing.union_all(incoming).subquery()

    # Subquery that returns customer ID and the number
    #  of distinct cities they've called
    customer_city_counts = (
        select(
            calls_per_city.c.customer_id,
            func.count(
                func.distinct(calls_per_city.c.city_id)
            ).label('city_count')
        )
        .group_by(calls_per_city.c.customer_id)
        .subquery()
    )

    # Total number of cities in the database subquery
    total_cities = select(func.count(City.id)).scalar_subquery()

    # Result query
    customers_with_all_cities = await session.scalars(
        select(Customer)
        .join(
            customer_city_counts,
            Customer.id == customer_city_counts.c.customer_id
        )
        .filter(
            customer_city_counts.c.city_count == total_cities  # type: ignore
        )
    )

    return [CustomerReadSchema.model_validate(customer)
            for customer in customers_with_all_cities]


@customer_router.get(
    '/monthly_call_sum/{customer_id:int}',
    response_model=list[MonthlyCallSumSchema],
    dependencies=[Depends(check_auth_token)]
)
async def get_monthly_call_sum(
        customer_id: int,
        session: Annotated[AsyncSession, Depends(get_session)]
) -> list[MonthlyCallSumSchema]:
    """Returns the total number of calls made by a customer in each month.

    :param customer_id: ID of the customer to return.
    :type customer_id: int
    :param session: SQLAlchemy AsyncSession instance.
    :type session: AsyncSession
    :return: Total number of calls made by a customer in each month.
    :rtype: list[MonthlyCallSumSchema]
    :raises HTTPException: If customer with such ID does not exist (404).
    """
    await pk_exists(session, Customer, customer_id)

    current_year = datetime.now().year
    call_year = extract('year', Call.started_at)
    call_month = extract('month', Call.started_at)

    results = await session.execute(
        select(
            call_month.label('month'),
            func.sum(Call.charge).label('total_charge')
        )
        .where(
            Call.from_customer_id == customer_id,
            Call.status == CallStatus.FINISHED,
            call_year == current_year
        )
        .group_by(call_month)
        .order_by(call_month)
    )

    return [
        MonthlyCallSumSchema(
            month=calendar.month_name[int(month_idx)],
            total_charge=total_charge
        )
        for month_idx, total_charge in results.all()
    ]


@customer_router.get(
    '/avg_call_charge_per_year',
    response_model=list[AvgCallChargePerYearSchema],
    dependencies=[Depends(check_auth_token)]
)
async def get_avg_call_charge_per_year(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> list[AvgCallChargePerYearSchema]:
    """Returns the average call charge per year for each customer.

    :return: Average call charge per year for each customer.
    :rtype: list[AvgCallChargePerYearSchema]
    """
    call_year = extract('year', Call.started_at)

    results = await session.execute(
        select(
            Customer,
            call_year,
            func.avg(Call.charge)
        )
        .join(Call, Call.from_customer_id == Customer.id)
        .filter(Call.status == CallStatus.FINISHED)
        .group_by(Customer.id, call_year)
        .order_by(call_year)
    )

    return [
        AvgCallChargePerYearSchema(
            year=year,
            avg_charge=avg_charge,
            customer=CustomerReadSchema.model_validate(customer)
        )
        for customer, year, avg_charge in results.all()
    ]


@customer_router.get(
    '/in_debt',
    response_model=list[InDebtCustomerSchema],
    dependencies=[Depends(check_auth_token)]
)
async def get_customers_in_debt(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> list[InDebtCustomerSchema]:
    """Returns a list of customers who have outstanding debt.

    :return: List of customers who have outstanding debt.
    :rtype: list[InDebtCustomerSchema]
    """
    # Payment sum for each customer
    payments_sum_subq = (
        select(
            Payment.customer_id.label('customer_id'),
            func.coalesce(func.sum(Payment.amount), 0).label('total_payments')
        )
        .group_by(Payment.customer_id)
        .subquery()
    )

    # Current debt for each customer
    debt_subq = (
        select(
            Customer.id.label('customer_id'),
            func.coalesce(payments_sum_subq.c.total_payments, 0).label('debt')
        )
        .outerjoin(
            payments_sum_subq,
            payments_sum_subq.c.customer_id == Customer.id  # type: ignore
        )
        .subquery()
    )

    # Max debt among all customers
    max_debt_subq = select(func.max(debt_subq.c.debt)).scalar_subquery()

    # Select customers with debt 70%-100% of the max debt
    results = await session.execute(
        select(Customer, debt_subq.c.debt)
        .join(
            debt_subq,
            debt_subq.c.customer_id == Customer.id  # type: ignore
        )
        .filter(
            debt_subq.c.debt >= 0.7 * max_debt_subq
        )
    )

    return [
        InDebtCustomerSchema(
            customer=CustomerReadSchema.model_validate(customer),
            debt=debt
        )
        for customer, debt in results.all()
    ]
