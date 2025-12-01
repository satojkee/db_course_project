from datetime import datetime, UTC

from sqlalchemy import (
    Integer, String,
    Float, ForeignKey,
    DateTime, Enum,
    Identity
)
from sqlalchemy.orm import (
    DeclarativeBase, mapped_column,
    Mapped, relationship
)

from app.types import CallStatus, PaymentStatus

__all__ = (
    'Base',
    'Customer',
    'City',
    'Country',
    'Category',
    'Rate',
    'PhoneNumber',
    'Call',
    'Payment',
    'Admin'
)


def utcnow() -> datetime:
    """Get the current date and time in UTC.

    :return: The current date and time in UTC.
    :rtype: datetime
    """
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models in this module."""


class _IDMixin:
    """Mixin class that adds an auto-incrementing primary key column."""

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(always=False),
        primary_key=True
    )


class Customer(_IDMixin, Base):
    __tablename__ = 'customers'

    fullname: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )
    passport: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True
    )
    city_id: Mapped[int] = mapped_column(
        ForeignKey('cities.id'),
        nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id'),
        nullable=False
    )

    # Relationships
    city: Mapped['City'] = relationship(
        'City',
        back_populates='customers'
    )
    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='customers'
    )
    phone_numbers: Mapped[list['PhoneNumber']] = relationship(
        'PhoneNumber',
        back_populates='customer',
    )
    payments: Mapped[list['Payment']] = relationship(
        'Payment',
        back_populates='customer',
    )
    outgoing_calls: Mapped[list["Call"]] = relationship(
        'Call',
        foreign_keys='Call.from_customer_id',
        back_populates='from_customer',
    )
    incoming_calls: Mapped[list["Call"]] = relationship(
        'Call',
        foreign_keys='Call.to_customer_id',
        back_populates='to_customer'
    )


class City(_IDMixin, Base):
    __tablename__ = 'cities'

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    zip_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey('countries.id'),
        nullable=False
    )

    # Relationships
    country: Mapped['Country'] = relationship(
        'Country',
        back_populates='cities'
    )
    customers: Mapped[list['Customer']] = relationship(
        'Customer',
        back_populates='city',
        cascade='all, delete-orphan'
    )


class Country(_IDMixin, Base):
    __tablename__ = 'countries'

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    minute_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    cities: Mapped[list['City']] = relationship(
        'City',
        back_populates='country',
        cascade='all, delete-orphan'
    )


class Category(_IDMixin, Base):
    __tablename__ = 'categories'

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    discount_mtp: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1
    )
    rate_id: Mapped[int] = mapped_column(
        ForeignKey('rates.id'),
        nullable=False
    )

    # Relationships
    rate: Mapped['Rate'] = relationship(
        'Rate',
        back_populates='categories'
    )
    customers: Mapped[list['Customer']] = relationship(
        'Customer',
        back_populates='category'
    )


class Rate(_IDMixin, Base):
    __tablename__ = 'rates'

    cost: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    # Relationships
    categories: Mapped[list['Category']] = relationship(
        'Category',
        back_populates='rate'
    )


class PhoneNumber(_IDMixin, Base):
    __tablename__ = 'phone_numbers'

    number: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        unique=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customers.id'),
        nullable=False
    )

    # Relationships
    customer: Mapped['Customer'] = relationship(
        'Customer',
        back_populates='phone_numbers'
    )


class Call(_IDMixin, Base):
    __tablename__ = 'calls'

    from_customer_id: Mapped[int] = mapped_column(
        ForeignKey('customers.id'),
        nullable=False
    )
    to_customer_id: Mapped[int] = mapped_column(
        ForeignKey('customers.id'),
        nullable=False
    )
    duration: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow
    )
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    charge: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )
    status: Mapped[str] = mapped_column(
        Enum(CallStatus, name='call_status', native_enum=True),
        nullable=False,
        default=CallStatus.IN_PROGRESS
    )

    # Relationships
    from_customer: Mapped["Customer"] = relationship(
        'Customer',
        foreign_keys=[from_customer_id],
        back_populates='outgoing_calls'
    )
    to_customer: Mapped["Customer"] = relationship(
        'Customer',
        foreign_keys=[to_customer_id],
        back_populates='incoming_calls'
    )


class Payment(_IDMixin, Base):
    __tablename__ = 'payments'

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('customers.id'),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(PaymentStatus, name='payment_status', native_enum=True),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    customer: Mapped['Customer'] = relationship(
        'Customer',
        foreign_keys=[customer_id],
        back_populates='payments'
    )


class Admin(_IDMixin, Base):
    __tablename__ = 'admins'

    username: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow
    )
