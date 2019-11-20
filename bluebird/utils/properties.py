"""
Contains property class definitions
"""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Optional, List

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


@dataclass
class AircraftProperties:
    """
    Dataclass representing all the properties of an aircraft. Equality is only computed
    by comparison with the Callsign
    """

    aircraft_type: str
    altitude: types.Altitude
    callsign: types.Callsign
    cleared_flight_level: types.Altitude
    ground_speed: types.GroundSpeed
    heading: types.Heading
    position: types.LatLon
    requested_flight_level: types.Altitude
    vertical_speed: types.VerticalSpeed

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.callsign == other.callsign


@dataclass
class RouteItem:
    waypoint: types.Waypoint
    required_gspd: Optional[types.GroundSpeed]


@dataclass
class AircraftRoute:

    callsign: types.Callsign
    segments: List[RouteItem]
    current_segment_index: int

    def __post_init__(self):
        assert self.current_segment_index < len(self.segments)
        # TODO(RKM 2019-11-19) Do we want to enforce that all waypoints have a specified
        # target altitude when being included in an aircraft's route?
        # for segment in self.segments:
        #     assert (
        #         segment.waypoint.altitude
        #     ), "Waypoint altitude must be set to be included in a route"


class SimState(IntEnum):
    """
    Simulator states
    """

    INIT = 1
    HOLD = 2
    RUN = 3
    END = 4


@dataclass(frozen=True)
class SimProperties:
    """Encapsulates the properties of the current simulation state"""

    scenario_name: str
    scenario_time: float  # The number of seconds since the start of the scenario
    seed: int
    speed: float
    state: SimState
    step_size: float
    utc_time: datetime

    def __post_init__(self):
        assert self.scenario_time >= 0, "Scanrio time must be positive"
        assert types.is_valid_seed(self.seed), "Invalid seed"
        assert self.speed >= 0, "Speed must be positive"
        assert self.step_size >= 0, "Step size must be positive"
