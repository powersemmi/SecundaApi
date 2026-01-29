from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.middleware.cors import CORSMiddleware

from api.routes.actiivty import router as activity_router
from api.routes.agency import router as agency_router
from api.routes.building import router as building_router
from api.settings import API_VERSION, SERVICE_NAME, settings

origins = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    app.state.engine = create_async_engine(
        settings.PG_URL.unicode_string(),
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    app.state.async_session = async_sessionmaker(
        bind=app.state.engine,
        expire_on_commit=False,
    )
    yield

    await app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        debug=settings.DEBUG,
        title=SERVICE_NAME,
        version=API_VERSION,
        lifespan=lifespan,
    )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> Any:
        return await request_validation_exception_handler(
            request, RequestValidationError(exc.errors())
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_router = APIRouter(prefix=settings.ROOT_PATH)
    api_router.include_router(agency_router)
    api_router.include_router(building_router)
    api_router.include_router(activity_router)
    app.include_router(api_router)

    return app


app = create_app()
