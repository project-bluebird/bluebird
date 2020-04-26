"""
Contains utility dataclasses representing physical units
"""
import re
from dataclasses import dataclass
from typing import Union

from bluebird.utils.units import METERS_PER_FOOT


_FL_REGEX = re.compile(r"^FL[0-9]\d*$")
_CALLSIGN_REGEX = re.compile(r"^[A-Z0-9]{3,}")


def is_valid_seed(seed: int) -> bool:
    """Checks if the given int is a valid seed"""
    # NOTE(RKM 2019-11-19) This is based on numpy's random seed range
    return not (seed < 0 or seed >> 32)


@dataclass(eq=True)
class Altitude:
    """
    Dataclass representing an altitude in feet
    """

    feet: int

    def __init__(self, alt: Union[int, str]):
        """
        :param alt: The altitude in feet (int) or FL (str)
        """

        assert alt is not None, "Altitude must be specified"
        if isinstance(alt, str):
            assert _FL_REGEX.match(alt), (
                "Altitude must be a valid flight level when passed as a string "
                f"(e.g. 'FL123'). Given '{alt}'"
            )
            self.feet = int(alt[2:]) * 100
        else:
            assert alt >= 0, "Altitude must be positive"
            self.feet = alt

    @property
    def meters(self) -> int:
        """
        The (rounded) altitude in meters
        """
        return int(self.feet * METERS_PER_FOOT)

    @property
    def flight_levels(self) -> str:
        """
        The altitude in flight levels
        """
        return f"FL{round(self.feet / 100)}"

    def __repr__(self):
        return str(self.feet)


@dataclass(eq=True)
class Callsign:
    """
    Dataclass representing an aircraft's callsign. Note that all callsigns will be
    converted to uppercase
    """

    value: str

    def __post_init__(self):
        self.value = self.value.upper()
        assert _CALLSIGN_REGEX.match(self.value), f"Invalid callsign '{self.value}'"

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return self.value


# TODO(RKM 2019-11-23) Add support for parsing Mach numbers
@dataclass(eq=True)
class GroundSpeed:
    """
    Dataclass representing an aircraft's ground speed [meters/sec]
    """

    meters_per_sec: float

    def __post_init__(self):
        assert isinstance(
            self.meters_per_sec, (float, int)
        ), "Ground speed must be numeric"
        assert self.meters_per_sec >= 0, "Ground speed must be positive"

    @property
    def feet_per_sec(self) -> int:
        """
        The (rounded) speed in feet per second
        """
        return int(self.meters_per_sec / METERS_PER_FOOT)

    def __repr__(self):
        return str(self.meters_per_sec)


@dataclass(eq=True)
class Heading:
    """
    Dataclass representing an aircraft's heading [°]
    """

    degrees: int

    def __post_init__(self):
        assert isinstance(self.degrees, int), "Heading must be an int"
        self.degrees = self.degrees % 360
        assert 0 <= self.degrees < 360, "Heading must satisfy 0 <= x < 360"

    def __repr__(self):
        return str(self.degrees)


@dataclass(eq=True)
class LatLon:
    """
    Dataclass representing a lat/lon pair
    """

    lat_degrees: float
    lon_degrees: float

    def __post_init__(self):
        assert isinstance(self.lat_degrees, (int, float)) and isinstance(
            self.lon_degrees, (int, float)
        )
        assert abs(self.lat_degrees) <= 90, "Latitude must satisfy abs(x) <= 90"
        assert abs(self.lon_degrees) <= 180, "Longitude must satisfy abs(x) <= 180"

    def __repr__(self):
        return f"{self.lat_degrees:f} {self.lon_degrees:f}"


@dataclass(eq=True)
class VerticalSpeed:
    """
    Dataclass representing a vertical speed [feet/min]
    """

    feet_per_min: int

    def __post_init__(self):
        assert isinstance(self.feet_per_min, int), "Vertical speed must be an integer"

    def __repr__(self):
        return str(self.feet_per_min)

    @staticmethod
    def from_meters_per_sec(vertical_speed):
        """
        Create a VerticalSpeed from a value in meters per second
        :param vertical_speed:
        :return:
        """
        return VerticalSpeed(vertical_speed * 60 / METERS_PER_FOOT)
