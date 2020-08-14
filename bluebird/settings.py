"""
Default settings for the BlueBird app
"""
# TODO Rename SIM_MODE
import logging
import os
from pathlib import Path

from semver import VersionInfo

from bluebird.utils.properties import SimMode
from bluebird.utils.properties import SimType


with open("VERSION") as version_file:
    _VERSION_STR = version_file.read().strip()
_VERSION = VersionInfo.parse(_VERSION_STR)


def in_agent_mode():
    """Checks if we are in Agent mode"""
    return Settings.SIM_MODE == SimMode.Agent


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
        LOGS_ROOT:          Root directory for log files. Defaults to ./logs
        CONSOLE_LOG_LEVEL:  The min. log level for console messages
        SIM_HOST:           Hostname of the simulation server
        SIM_MODE:           Mode for interacting with the simulator
        SIM_TYPE:           The simulator type
        BS_EVENT_PORT:      BlueSky event port
        BS_STREAM_PORT:     BlueSky stream port
        BS_TIMEOUT:         Max. time to wait for BlueSky to respond
        MC_PORT:            MachineCollege port
    """

    VERSION: VersionInfo = _VERSION
    API_VERSION: int = _VERSION.major
    FLASK_DEBUG: bool = True
    PORT: int = int(os.getenv("BB_PORT", 5001))

    DATA_DIR = Path("data")

    SIM_LOG_RATE: float = 0.2
    LOGS_ROOT: str = Path(os.getenv("BB_LOGS_ROOT", "logs"))
    CONSOLE_LOG_LEVEL: int = logging.DEBUG

    SIM_HOST: str = "localhost"
    SIM_MODE: SimMode = SimMode.Agent
    SIM_TYPE: SimType = SimType.BlueSky

    # BlueSky settings
    BS_EVENT_PORT: int = int(os.getenv("BS_EVENT_PORT", 9000))
    BS_STREAM_PORT: int = int(os.getenv("BS_STREAM_PORT", 9001))
    BS_STREAM_TIMEOUT: int = 5
    BS_TIMEOUT: int = 10

    # MachColl settings
    MC_PORT: int = 5321
