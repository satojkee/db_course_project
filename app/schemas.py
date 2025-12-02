from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.types import CallStatusesLiteral, PaymentStatusesLiteral

__all__ = (
    'CustomerCreateSchema',
    'RateCreateSchema',
    'PhoneCreateSchema',
    'CityCreateSchema',
    'CountryCreateSchema',
    'CategoryCreateSchema',
    'CityUpdateSchema',
    'RateUpdateSchema',
    'CountryUpdateSchema',
    'CustomerUpdateSchema',
    'CategoryUpdateSchema',
    'RateReadSchema',
    'CityReadSchema',
    'PhoneReadSchema',
    'CountryReadSchema',
    'CategoryReadSchema',
    'CustomerReadSchema',
    'CustomerCityPairSchema',
    'AvgCallChargePerYearSchema',
    'CallCreateSchema',
    'CallReadSchema',
    'CallUpdateSchema',
    'MonthlyCallSumSchema',
    'InDebtCustomerSchema',
    'TopCitySchema',
    'PaymentReadSchema',
    'LoginSchema',
    'TokenReadSchema'
)


class _BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')


class _BaseCustomerSchema(_BaseSchema):
    fullname: str = Field(..., max_length=128)
    city_id: int
    category_id: int


class _IDMixin(BaseModel):
    id: int = Field(..., ge=1)


class CountryCreateSchema(_BaseSchema):
    name: str = Field(..., max_length=256)
    minute_cost: float


class CityCreateSchema(_BaseSchema):
    name: str = Field(..., max_length=256)
    zip_code: str = Field(..., max_length=50)
    country_id: int


class CategoryCreateSchema(_BaseSchema):
    name: str = Field(..., max_length=256)
    discount_mtp: float = Field(..., gt=0)
    rate_id: int


class CustomerCreateSchema(_BaseCustomerSchema):
    passport: str = Field(..., max_length=11)


class RateCreateSchema(_BaseSchema):
    cost: float


class CallCreateSchema(_BaseSchema):
    from_customer_id: int
    to_customer_id: int


class PhoneCreateSchema(_BaseSchema):
    number: str = Field(..., max_length=15)
    customer_id: int


class CountryUpdateSchema(_BaseSchema):
    minute_cost: float


class CityUpdateSchema(_BaseSchema):
    name: str | None = Field(None, max_length=256)
    zip_code: str | None = Field(None, max_length=50)


class CategoryUpdateSchema(_BaseSchema):
    name: str | None = Field(None, max_length=256)
    discount_mtp: float | None = Field(None, gt=0)
    rate_id: int | None = Field(None, ge=1)


class CustomerUpdateSchema(_BaseSchema):
    fullname: str | None = Field(None, max_length=128)
    city_id: int | None = Field(None, ge=1)
    category_id: int | None = Field(None, ge=1)
    passport: str | None = Field(None, max_length=11)


class CallUpdateSchema(_BaseSchema):
    status: CallStatusesLiteral


class RateUpdateSchema(RateCreateSchema):
    ...


class CountryReadSchema(CountryCreateSchema, _IDMixin):
    ...


class CityReadSchema(CityCreateSchema, _IDMixin):
    ...


class CategoryReadSchema(CategoryCreateSchema, _IDMixin):
    ...


class CustomerReadSchema(_BaseCustomerSchema, _IDMixin):
    ...


class RateReadSchema(RateCreateSchema, _IDMixin):
    ...


class PhoneReadSchema(PhoneCreateSchema, _IDMixin):
    ...


class PaymentReadSchema(_BaseSchema, _IDMixin):
    amount: float
    customer_id: int
    status: PaymentStatusesLiteral
    created_at: datetime
    updated_at: datetime | None = None


class CallReadSchema(CallCreateSchema, _IDMixin):
    status: CallStatusesLiteral
    duration: float
    charge: float


class CustomerCityPairSchema(_BaseSchema):
    customer: CustomerReadSchema
    city: CityReadSchema
    total_calls: int


class AvgCallChargePerYearSchema(_BaseSchema):
    avg_charge: float
    year: int
    customer: CustomerReadSchema


class MonthlyCallSumSchema(_BaseSchema):
    month: str
    total_charge: float


class InDebtCustomerSchema(_BaseSchema):
    customer: CustomerReadSchema
    debt: float


class TopCitySchema(_BaseSchema):
    city: CityReadSchema
    internal_calls: int


class LoginSchema(_BaseSchema):
    username: str = Field(..., max_length=32)
    password: str = Field(..., max_length=32)


class TokenReadSchema(_BaseSchema):
    access_token: str
    token_type: str
