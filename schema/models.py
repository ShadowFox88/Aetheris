from __future__ import annotations

import datetime  # noqa: TC003 # we need this for mapped

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import BigInteger


class Base(DeclarativeBase):
    """
    A base class for all models. Used for type hinting.
    """

    __abstract__ = True

    record_created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    record_updated_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )


def serialise(obj: type[Base]) -> dict[str, str | int | bool | None]:
    """
    Serialise a model object to a dictionary.
    """
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


class User(Base):
    """
    A default user model.
    """

    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    administrator: Mapped[bool] = mapped_column(default=False)


class File(Base):
    """
    A default file model.
    """

    __tablename__ = "Files"

    id: Mapped[str] = mapped_column(primary_key=True)
    original_name: Mapped[str] = mapped_column(unique=True)
    date_uploaded: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    mimetype: Mapped[str] = mapped_column(server_default="application/octet-stream")
    size: Mapped[int] = mapped_column()

    views: Mapped[int] = mapped_column(server_default=text("0"))

    date_expires: Mapped[datetime.datetime | None] = mapped_column(server_default=None)
    password: Mapped[str | None] = mapped_column(server_default=None)

    owner: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    note: Mapped[str | None] = mapped_column(server_default=None)
