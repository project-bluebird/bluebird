"""
Contains utility dataclasses representing physical units
"""


from dataclasses import dataclass
from typing import Union
import re

_METERS_PER_FOOT = 0.3048


@dataclass
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
            assert re.match(r"^FL[1-9]\d*$", alt), (
                "Altitude must be a valid flight level when passed as a string "
                '(e.g. "FL123")'
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
    def flight_level(self) -> str:
        """
        The altitude in flight levels
        """
        return f"FL{round(self.feet / 100)}"

    def __str__(self) -> str:
        return str(self.feet)


@dataclass
class Callsign:
    """
    Dataclass representing an aircraft's callsign
    """

    value: str

    def __init__(self, callsign: str):
        assert re.match(
            r"[a-z0-9]{3,}", callsign, re.IGNORECASE
        ), f"Invalid callsign {callsign}"
        self.value = callsign

    def __repr__(self) -> str:
        return self.value


@dataclass
class GroundSpeed:
    """
    Dataclass representing an aircraft's ground speed [meters/sec]
    """

    meters_per_sec: int

    def __init__(self, ground_speed: int):
        assert ground_speed >= 0, "Ground speed must be positive"
        self.meters_per_sec = ground_speed

    @property
    def feet_per_sec(self) -> int:
        """
        The (rounded) speed in feet per second
        """
        return int(self.meters_per_sec / _METERS_PER_FOOT)

    def __repr__(self) -> str:
        return str(self.meters_per_sec)


@dataclass
class Heading:
    """
    Dataclass representing an aircraft's heading [°]
    """

    heading_degrees: int

    def __init__(self, heading: int):
        assert 0 <= heading < 360, "Heading must satisfy 0 <= x < 360"
        self.heading_degrees = heading

    def __repr__(self) -> str:
        return str(self.heading_degrees)


@dataclass
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

    def __repr__(self) -> str:
        return f"{self.lat_degrees:f} {self.lon_degrees:f}"


@dataclass
class VerticalSpeed:
    """
    Dataclass representing a vertical speed [m/s]
    """

    meters_per_sec: int

    def __init__(self, vertical_speed: int):
        self.meters_per_sec = vertical_speed

    def feet_per_sec(self) -> int:
        """
        The (rounded) speed in feet per second
        """
        return int(self.meters_per_sec / _METERS_PER_FOOT)

    def __repr__(self) -> str:
        return str(self.meters_per_sec)
