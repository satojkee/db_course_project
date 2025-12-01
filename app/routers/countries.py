from fastcrud import crud_router

from app.dependencies import get_session, check_auth_token
from app.schemas import (
    CountryCreateSchema,
    CountryUpdateSchema,
    CountryReadSchema
)
from app.orm.models import Country

__all__ = ('country_router',)

# Dependencies for all endpoints
deps = [check_auth_token]

country_router = crud_router(
    session=get_session,
    model=Country,
    select_schema=CountryReadSchema,
    create_schema=CountryCreateSchema,
    update_schema=CountryUpdateSchema,
    path='/countries',
    tags=['Countries'],
    delete_deps=deps,
    create_deps=deps,
    update_deps=deps,
    read_deps=deps,
    read_multi_deps=deps
)
