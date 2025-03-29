from litestar import Router, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN
from schema.models import User
from schema.return_models import UserTypeInput, UserTypeReturn
from server.settings import (
    PUBLIC_REGISTRATION,
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils.snowflake import SnowflakeGenerator


@post("/register", exclude_from_auth=True)
async def register(
    data: UserTypeInput,
    snowflake_generator: SnowflakeGenerator,
    transaction: AsyncSession,
) -> UserTypeReturn:
    """
    Register a new user.
    """
    if PUBLIC_REGISTRATION is False:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Public registration is disabled.",
        )
    new_user = User(
        username=data.username,
        password=data.password,
        id=snowflake_generator.generate(),
    )
    transaction.add(new_user)

    return UserTypeReturn(username=new_user.username, id=new_user.id)


user_router = Router(path="/user", route_handlers=[register])
