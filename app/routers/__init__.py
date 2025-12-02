from fastapi import APIRouter

from .auth import auth_router
from .calls import call_router
from .rates import rate_router
from .cities import city_router
from .countries import country_router
from .customers import customer_router
from .categories import category_router
from .phone_numbers import phone_router
from .payments import payment_router

__all__ = ('v1_router',)

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(auth_router)
v1_router.include_router(category_router)
v1_router.include_router(rate_router)
v1_router.include_router(city_router)
v1_router.include_router(country_router)
v1_router.include_router(customer_router)
v1_router.include_router(phone_router)
v1_router.include_router(call_router)
v1_router.include_router(payment_router)
