import datetime
import pathlib
import secrets
import socket
import os

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


def is_docker() -> bool:
    """
    Check if a function is running in a docker container.
    """
    path = pathlib.Path("/proc/self/cgroup")
    docker_env = pathlib.Path("/.dockerenv")
    return docker_env.exists() or (
        path.is_file() and any("docker" in line for line in path.open())
    )

def is_kubernetes() -> bool:
    """
    Check if a function is running in a kubernetes container.
    """
    path = pathlib.Path("/var/run/secrets/kubernetes.io") # https://stackoverflow.com/a/49045575

    return path.exists() or os.getenv("KUBERNETES_SERVICE_HOST") is not None

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
        self.__machine_id: int = self.get_machine_id()
        self._machine_id: int = self.within_range(self.__machine_id, 5)
        self._random: int = secrets.randbelow(1 << 5)

    def get_machine_id(self) -> int:
        """
        Get the machine id.
        """
        if is_docker():
            return int(
                socket.gethostname(),
                16,  # random hex in docker
            )
        if is_kubernetes():
            name = socket.gethostname()
            return int(
                name.split("-")[1],
                16,  # random hex in kubernetes
            )

        # how have you done this... it should ONLY be run in k8s or docker but whatever
        return secrets.randbelow(1 << 5)

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
