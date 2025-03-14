from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Literal

from litestar import Litestar, get
from litestar.datastructures import ResponseHeader, State
from litestar.exceptions import HTTPException
from litestar.middleware.base import DefineMiddleware
from litestar.status_codes import HTTP_409_CONFLICT
from server.auth.middleware import TokenAuthMiddleware
from server.settings import DEBUG, INSTANCE_ID, OPENAPI_CONFIG
from server.v1 import v1_router
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils.snowflake import SnowflakeGenerator


@get("/", exclude_from_auth=True)
async def welcome() -> Literal["Welcome to Aetheris, an Image Sharing API!"]:
    """
    Display the home page of the API.
    """
    return "Welcome to Aetheris, an Image Sharing API!"


@get("/ping", exclude_from_auth=True)
async def ping() -> None:
    """
    Return a 200 OK response to indicate the server is running.
    """
    return

@get("/id", exclude_from_auth=True)
async def instance_id() -> str:
    """
    Return the instance ID.
    """
    return INSTANCE_ID


middleware = [DefineMiddleware(TokenAuthMiddleware, exclude="docs")]


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    """
    Lifespan handler to create and dispose of the database connection.
    """
    engine: Any | None = getattr(app.state, "engine", None)
    if engine is None:
        engine = create_async_engine(
            "postgresql+asyncpg://Aetheris:Aetheris@db:5432/Aetheris"
        )
        app.state.engine = engine

    try:
        yield
    finally:
        await engine.dispose()


def create_app() -> Litestar:
    """
    Create the Litestar app.
    """
    snowflake_generator = SnowflakeGenerator()
    sessionmaker = async_sessionmaker()

    async def provide_snowflake_generator() -> SnowflakeGenerator:
        return snowflake_generator

    async def provide_transaction(state: State) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker(bind=state.engine) as session:
            try:
                async with session.begin():
                    yield session
            except IntegrityError as exc:
                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail=str(exc),
                ) from exc

    return Litestar(
        route_handlers=[welcome, v1_router()],
        debug=DEBUG,
        openapi_config=OPENAPI_CONFIG,
        middleware=middleware,
        lifespan=[db_connection],
        dependencies={
            "snowflake_generator": provide_snowflake_generator,
            "transaction": provide_transaction,
        },
        response_headers=[
            ResponseHeader(name="X-ID", value=INSTANCE_ID),
        ]
    )


app: Litestar = create_app()
