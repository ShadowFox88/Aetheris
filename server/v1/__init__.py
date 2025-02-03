"""
Registers all the routes for the v1 of the application.
"""

from litestar import Router
from server.v1.routes.user import user_router


def v1_router() -> Router:
    """
    Create the router for v1 of the api.
    """
    return Router(path="/v1", route_handlers=[user_router])
