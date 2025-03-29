import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Literal

from litestar import Litestar, get
from litestar.datastructures import ResponseHeader, State
from litestar.exceptions import HTTPException
from litestar.middleware.base import DefineMiddleware
from litestar.plugins.sqlalchemy import SQLAlchemySerializationPlugin
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.types.protocols import Logger
from schema.models import Base
from server.auth.middleware import TokenAuthMiddleware
from server.settings import (
    CONTACT_EMAIL,
    CONTACT_NAME,
    DEBUG,
    INSTANCE_ID,
    LOGGING_CONFIG,
    OPENAPI_CONFIG,
    PUBLIC_REGISTRATION,
    VERSION,
)
from server.v1 import v1_router
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from utils.snowflake import SnowflakeGenerator

logger: Logger = LOGGING_CONFIG.configure()()


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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await engine.dispose()


async def startup() -> None:
    """
    Log some information about the app on startup.
    """
    logger.info("Creating the Litestar app.")
    logger.info(f"""
    Version: {VERSION}

    Debug Mode: {"Enabled" if DEBUG else "Disabled"}
    Public Registration: {"Enabled" if PUBLIC_REGISTRATION else "Disabled"}
    Instance ID: {INSTANCE_ID}
    Contact Name: {CONTACT_NAME}
    Contact Email: {CONTACT_EMAIL}

    """)  # noqa: G004

    if DEBUG:
        logging.debug("Debug Message.")
        logging.info("Info Message.")
        logging.warning("Warning Message.")
        logging.error("Error Message.")
        logging.critical("Critical Message.")


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
        logging_config=LOGGING_CONFIG,
        middleware=middleware,
        lifespan=[db_connection],
        dependencies={
            "snowflake_generator": provide_snowflake_generator,
            "transaction": provide_transaction,
        },
        on_startup=[startup],
        response_headers=[
            ResponseHeader(name="X-Instance-ID", value=INSTANCE_ID),
        ],
        plugins=[SQLAlchemySerializationPlugin()],
    )


app: Litestar = create_app()
