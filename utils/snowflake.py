import datetime
import secrets
import socket

EPOCH: datetime.datetime = datetime.datetime(
    year=2008,
    month=9,
    day=21,
    hour=5,
    minute=22,
    second=0,
    tzinfo=datetime.timezone.utc,
)

# 42 bits for timestamp
# 5 bits for machine id
# 5 bits for random number
# 12 bits for increment


class SnowflakeGenerator:
    """
    A class to generate snowflakes.
    """

    def __init__(self) -> None:
        """
        Set the initial values for the snowflake generator.
        """
        self._increment: int = 0
        self._epoch: datetime.datetime = EPOCH
        self.__machine_id: int = int(
            socket.gethostname(),
            16,  # random hex in docker
        )
        self._machine_id: int = self.within_range(self.__machine_id, 5)
        self._random: int = secrets.randbelow(1 << 5)

    def within_range(self, number: int, bits: int) -> int:
        """
        Ensure a number is within the range of a certain number of bits.
        """
        return number & ((1 << bits) - 1)

    def generate(self) -> int:
        """
        Generate a snowflake.
        """
        temp: datetime.timedelta = datetime.datetime.now(tz=datetime.UTC) - self._epoch
        timestamp = int(
            ((temp.days * 86400 + temp.seconds) * 10**6 + temp.microseconds) / 10**3
        )
        snowflake: int = (
            (timestamp << 22)
            | (self._random << 17)
            | (self._machine_id << 12)
            | self._increment
        )

        self._increment = self.within_range(self._increment + 1, 12)
        return snowflake
