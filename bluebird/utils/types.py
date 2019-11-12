"""
Contains utility dataclasses representing physical units
"""

from dataclasses import dataclass
import re
from typing import Optional, Union


_METERS_PER_FOOT = 0.3048

_FL_REGEX = re.compile(r"^FL[1-9]\d*$")
_CALLSIGN_REGEX = re.compile(r"^[A-Z0-9]{3,}")


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
        return int(self.feet * _METERS_PER_FOOT)

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

    def __init__(self, callsign: str):
        callsign = callsign.upper()
        assert _CALLSIGN_REGEX.match(callsign), f"Invalid callsign {callsign}"
        self.value = callsign

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return self.value


@dataclass(eq=True)
class GroundSpeed:
    """
    Dataclass representing an aircraft's ground speed [meters/sec]
    """

    meters_per_sec: int

    def __init__(self, ground_speed: int):
        assert isinstance(ground_speed, int), "Ground speed must be an int"
        assert ground_speed >= 0, "Ground speed must be positive"
        self.meters_per_sec = ground_speed

    @property
    def feet_per_sec(self) -> int:
        """
        The (rounded) speed in feet per second
        """
        return int(self.meters_per_sec / _METERS_PER_FOOT)

    def __repr__(self):
        return str(self.meters_per_sec)


@dataclass(eq=True)
class Heading:
    """
    Dataclass representing an aircraft's heading [°]
    """

    degrees: int

    def __init__(self, heading: int):
        assert isinstance(heading, int), "Heading must be an int"
        assert 0 <= heading < 360, "Heading must satisfy 0 <= x < 360"
        self.degrees = heading

    def __repr__(self):
        return str(self.degrees)


@dataclass(eq=True)
class LatLon:
    """
    Dataclass representing a lat/lon pair
    """

    lat_degrees: float
    lon_degrees: float

    def __init__(self, lat: float, lon: float):
        assert abs(lat) <= 90, "Latitude must satisfy abs(x) <= 90"
        assert abs(lon) <= 180, "Longitude must satisfy abs(x) <= 180"
        self.lat_degrees, self.lon_degrees = (lat, lon)

    def __repr__(self):
        return f"{self.lat_degrees:f} {self.lon_degrees:f}"


@dataclass(eq=True)
class VerticalSpeed:
    """
    Dataclass representing a vertical speed [feet/min]
    """

    feet_per_min: int

    def __init__(self, vertical_speed: int):
        assert isinstance(vertical_speed, int), "Vertical speed must be an integer"
        self.feet_per_min = vertical_speed

    def __repr__(self):
        return str(self.feet_per_min)

    @staticmethod
    def from_meters_per_sec(vertical_speed):
        """
        Create a VerticalSpeed from a value in meters per second
        :param vertical_speed:
        :return:
        """
        return VerticalSpeed(vertical_speed * 60 / _METERS_PER_FOOT)


@dataclass(eq=True)
class Waypoint:
    """
    Dataclass representing a named waypoint and optional altitude. __repr__ returns the
    waypoint name
    """

    name: str
    position: LatLon
    altitude: Optional[Altitude]

    def __repr__(self):
        return self.name
