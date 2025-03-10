from __future__ import annotations

import os
import secrets

from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import (
    JsonRenderPlugin,
    ScalarRenderPlugin,
    YamlRenderPlugin,
)
from litestar.openapi.spec import Components, Contact, License, Server

VERSION = "0.1.0"  # I change this manually to reflect pyproject.toml

DEBUG: bool = os.getenv("DEBUG") in ("True", "true", "1")

CONTACT_NAME: str | None = os.getenv("CONTACT_NAME")
CONTACT_EMAIL: str | None = os.getenv("CONTACT_EMAIL")
CONTACT_URL: str | None = os.getenv("CONTACT_URL")

PUBLIC_REGISTRATION: bool = os.getenv("PUBLIC_REGISTRATION") in ("True", "true", "1")

INSTANCE_ID: str = secrets.token_hex(8)

OPENAPI_CONFIG: OpenAPIConfig = OpenAPIConfig(
    path="docs",
    title="Aetheris",
    version=VERSION,
    create_examples=True,
    random_seed=88,
    contact=Contact(
        name=CONTACT_NAME,
        email=CONTACT_EMAIL,
        url=CONTACT_URL,
    ),
    description="An Image Sharing API",
    license=License(
        name="GNU Affero General Public License v3", identifier="AGPL-3.0-or-later"
    ),
    components=Components(  # stolen from default
        schemas={},  # used by litestar.app.Litestar
        responses=None,
        parameters=None,
        examples=None,
        request_bodies=None,
        headers=None,
        security_schemes=None,
        links=None,
        callbacks=None,
        path_items=None,
    ),
    servers=[Server(url="/", description=None, variables=None)],
    use_handler_docstrings=True,
    render_plugins=[
        ScalarRenderPlugin(path="/"),
        YamlRenderPlugin(),
        JsonRenderPlugin(),
    ],  # pyright: ignore[reportArgumentType] # i just like scalar
    enabled_endpoints={"openapi.yml", "openapi.json", "openapi.yaml"},
)
