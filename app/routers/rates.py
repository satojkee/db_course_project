from fastcrud import crud_router

from app.dependencies import get_session, check_auth_token
from app.schemas import (
    RateCreateSchema,
    RateUpdateSchema,
    RateReadSchema
)
from app.orm.models import Rate

__all__ = ('rate_router',)

# Dependencies for all endpoints
deps = [check_auth_token]

rate_router = crud_router(
    session=get_session,
    model=Rate,
    select_schema=RateReadSchema,
    create_schema=RateCreateSchema,
    update_schema=RateUpdateSchema,
    path='/rates',
    tags=['Rates'],
    read_deps=deps,
    read_multi_deps=deps,
    create_deps=deps,
    update_deps=deps,
    delete_deps=deps
)
