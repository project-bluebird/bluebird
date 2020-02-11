"""
Contains property class definitions
"""
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any
from typing import Dict
from typing import Optional

from aviary.sector.sector_element import SectorElement

import bluebird.utils.types as types


# TODO Figure out if the common "_missing_" function can be refactored out
class SimMode(IntEnum):
    """
    BlueBird's operating modes

    Attributes:
        Sandbox:    Default. Simulation runs normally
        Agent:      Simulation starts paused and must be manually advanced with STEP
    """

    Sandbox = 1
    Agent = 2

    @classmethod
    def _missing_(cls: type(IntEnum), value: str):
        for member in cls:
            if SimMode(member).name.lower() == value.lower():
                return member
        raise ValueError(
            f'SimMode has no value "{value}". Options are - '
            f'{", ".join(cls.__members__)}'
        )


class SimType(IntEnum):
    """
    Supported simulators

    Attributes:
        BlueSky:    Default. The open-source BlueSky simulator
        MachColl:   The Machine College simulator
    """

    BlueSky = 1
    MachColl = 2

    @classmethod
    def _missing_(cls: type(IntEnum), value: str):
        for member in cls:
            if SimType(member).name.lower() == value.lower():
                return member
        raise ValueError(
            f'SimType has no value "{value}". Options are - '
            f'{", ".join(cls.__members__)}'
        )


class SimState(IntEnum):
    """Simulator states"""

    INIT = 1
    HOLD = 2
    RUN = 3
    END = 4


@dataclass
class SimProperties:
    """Encapsulates the properties of the current simulation state"""

    sector_name: Optional[str]
    scenario_name: Optional[str]
    scenario_time: float  # The number of seconds since the start of the scenario
    seed: Optional[int]
    speed: float  # In agent mode, this is the step size
    state: SimState
    dt: float
    utc_datetime: datetime

    def __post_init__(self):
        assert self.scenario_time >= 0, "Scanrio time must be positive"
        if self.seed is not None:
            assert types.is_valid_seed(self.seed), "Invalid seed"
        assert self.speed >= 0, "Speed must be positive"
        assert self.dt >= 0, "Dt must be positive"


@dataclass
class Scenario:
    name: str
    content: Optional[Dict[str, Any]]


@dataclass
class Sector:
    name: str
    element: Optional[SectorElement]


@dataclass(eq=True)
class AircraftProperties:
    """Dataclass representing all the properties of an aircraft"""

    aircraft_type: str
    altitude: types.Altitude
    callsign: types.Callsign
    cleared_flight_level: types.Altitude
    ground_speed: types.GroundSpeed
    heading: types.Heading
    position: types.LatLon
    requested_flight_level: types.Altitude
    route_name: Optional[str]
    vertical_speed: types.VerticalSpeed
    initial_flight_level: types.Altitude

    def __post_init__(self):
        assert self.aircraft_type, "Aircraft type must be defined"

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> "AircraftProperties":
        """
        Create an AircraftProperties from the current sector element and an "aircraft"
        object from the scenario json
        """
        return cls(
            aircraft_type=data["type"],
            altitude=types.Altitude(data["currentFlightLevel"]),
            callsign=types.Callsign(data["callsign"]),
            cleared_flight_level=types.Altitude(data["clearedFlightLevel"]),
            ground_speed=None,
            # TODO(rkm 2020-01-22) Check if we should know the initial heading here
            heading=None,
            position=types.LatLon(data["startPosition"][1], data["startPosition"][0]),
            requested_flight_level=types.Altitude(data["requestedFlightLevel"]),
            route_name=None,
            vertical_speed=None,
            initial_flight_level=types.Altitude(data["currentFlightLevel"]),
        )
