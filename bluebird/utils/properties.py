"""
Contains property definitions
"""

# TODO Figure out if the common "_missing_" function can be refactored out

from enum import IntEnum


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
    def _missing_(cls, value):
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
    def _missing_(cls, value):
        for member in cls:
            if SimType(member).name.lower() == value.lower():
                return member
        raise ValueError(
            f'SimType has no value "{value}". Options are - '
            f'{", ".join(cls.__members__)}'
        )
