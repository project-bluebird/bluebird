"""
Contains property class definitions
"""

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum

from bluebird.utils.types import (
    Altitude,
    Callsign,
    GroundSpeed,
    Heading,
    LatLon,
    VerticalSpeed,
)


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


# TODO Needs to (possibly) include route information
@dataclass
class AircraftProperties:
    """
    Dataclass representing all the properties of an aircraft. Equality is only computed
    by comparison with the Callsign
    """

    aircraft_type: str
    altitude: Altitude
    callsign: Callsign
    cleared_flight_level: Altitude
    ground_speed: GroundSpeed
    heading: Heading
    position: LatLon
    requested_flight_level: Altitude
    vertical_speed: VerticalSpeed

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.callsign == other.callsign


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
    state: SimState
    speed: float
    step_size: float
    time: float
    # time_utc: datetime  # TODO Not sure if this is needed
    scn_name: str
