from dataclasses import dataclass


@dataclass
class UserTypeInput:
    """
    A type hint for making a user.
    """

    username: str
    password: str


@dataclass
class UserTypeReturn:
    """
    A type hint for making a user.
    """

    id: int
    username: str
