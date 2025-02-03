from typing import Any

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

API_HEADER = "X-API-Key"


class TokenAuthMiddleware(AbstractAuthenticationMiddleware):
    """
    Custom Middleware To Authenticate Requests Using API Tokens.
    """

    async def authenticate_request(
        self, connection: ASGIConnection[Any, Any, Any, Any]
    ) -> AuthenticationResult:
        """
        Authenticate the request using the API token.
        """
        tokens = ["a", "b"]

        provided_token = connection.headers.get(API_HEADER)

        if not provided_token:
            raise NotAuthorizedException

        if provided_token not in tokens:
            raise NotAuthorizedException
        return AuthenticationResult(user="api", auth=provided_token)
