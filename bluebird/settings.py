"""
Default settings for the BlueBird app
"""

# TODO Rename SIM_MODE

from abc import ABC
import os

import logging
from semver import VersionInfo

from bluebird.utils.properties import SimMode, SimType


with open("VERSION") as version_file:
    _VERSION_STR = version_file.read().strip()


class Settings(ABC):  # pylint: disable=too-few-public-methods
    """
    BlueBird's settings

    Attributes:
        VERSION:            BlueBird release version
        API_VERSION:        BlueBird API version
        FLASK_DEBUG:        FLASK_DEBUG flag for `Flask.run(debug=FLASK_DEBUG)`
        PORT:               BlueBird (Flask) server port
        SIM_LOG_RATE:       Rate (in sim-seconds) at which aircraft data is logged to
                            the episode file
        LOGS_ROOT:          Root directory for log files
        CONSOLE_LOG_LEVEL:  The min. log level for console messages
        METRICS_PROVIDERS:  List of package names containing metrics providers
        SIM_HOST:           Hostname of the simulation server
        SIM_MODE:           Mode for interacting with the simulator
        SIM_TYPE:           The simulator type
        BS_EVENT_PORT:      BlueSky event port
        BS_STREAM_PORT:     BlueSky stream port
    """

    VERSION = VersionInfo.parse(_VERSION_STR)
    API_VERSION = 1
    FLASK_DEBUG = True
    PORT = 5001

    SIM_LOG_RATE = 0.2
    LOGS_ROOT = os.getenv("BB_LOGS_ROOT", "logs")
    CONSOLE_LOG_LEVEL = logging.INFO

    METRICS_PROVIDERS = ["bluebird"]

    SIM_HOST = "localhost"
    # SIM_PORT = 123 - MachColl?
    SIM_MODE = SimMode.Sandbox
    SIM_TYPE = SimType.BlueSky

    @staticmethod
    def set_sim_mode(new_val: str):
        """
        Update the current sim mode setting
        :raises ValueError: If the given string is not a valid mode
        """
        try:
            Settings.SIM_MODE = SimMode(new_val)
        except KeyError as exc:
            raise ValueError(
                f'Mode "{new_val}" not supported. Must be one of: '
                f'{", ".join([x.name for x in SimMode])}'
            ) from exc

    @staticmethod
    def set_sim_type(new_val: str):
        """
        Update the current sim type setting
        :raises ValueError: If the given string is not a valid type
        """
        try:
            Settings.SIM_TYPE = SimType(new_val)
        except KeyError as exc:
            raise ValueError(
                f'Type "{new_val}" not supported. Must be one of: '
                f'{", ".join([x.name for x in SimType])}'
            ) from exc

    # TODO Move to subclass
    BS_EVENT_PORT = 9000
    BS_STREAM_PORT = 9001
