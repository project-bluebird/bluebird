"""
Default settings for the BlueBird app
"""
# TODO Rename SIM_MODE
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from semver import VersionInfo

from bluebird.utils.properties import SimMode
from bluebird.utils.properties import SimType

with open("VERSION") as version_file:
    _VERSION_STR = version_file.read().strip()
_VERSION = VersionInfo.parse(_VERSION_STR)


def in_agent_mode():
    """Checks if we are in Agent mode"""
    return Settings.SIM_MODE == SimMode.Agent


def time_for_logfile():
    """Returns the current timestamp formatted for a logfile name"""
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


class Settings:
    """
    BlueBird's settings. Should be treated as a static singleton object.

    Attributes:
        VERSION:            BlueBird release version
        API_VERSION:        BlueBird API version
        FLASK_DEBUG:        FLASK_DEBUG flag for `Flask.run(debug=FLASK_DEBUG)`
        PORT:               BlueBird (Flask) server port
        SIM_LOG_RATE:       Rate (in sim-seconds) at which aircraft data is logged to
                            the episode file
        DATA_DIR:           BlueBird's data directory
        INSTANCE_ID:        The current instance UUID

        SIM_HOST:           Hostname of the simulation server
        SIM_MODE:           Mode for interacting with the simulator
        SIM_TYPE:           The simulator type
        BS_EVENT_PORT:      BlueSky event port
        BS_STREAM_PORT:     BlueSky stream port
        MC_PORT:            MachineCollege port
    """

    VERSION: VersionInfo = _VERSION
    API_VERSION: int = _VERSION.major
    FLASK_DEBUG: bool = True
    PORT: int = 5001

    DATA_DIR = Path("data")
    INSTANCE_ID = uuid.uuid1()  # TODO(rkm 2020-02-10) Type?
    INST_LOG_DIR: Optional[Path] = None

    SIM_LOG_RATE: float = 0.2

    SIM_HOST: str = "localhost"
    SIM_MODE: SimMode = SimMode.Agent
    SIM_TYPE: SimType = SimType.BlueSky

    # TODO Move to subclass
    BS_EVENT_PORT: int = 9000
    BS_STREAM_PORT: int = 9001
    MC_PORT: int = 5321
