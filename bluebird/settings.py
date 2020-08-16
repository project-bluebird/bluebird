"""
Default settings for the BlueBird app
"""
import functools
import logging
import os
from pathlib import Path
from typing import Any
from typing import Dict
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


def current_settings() -> Dict[str, Any]:
    """Returns the current Settings as a dict"""
    ret = {}
    for s in dir(Settings):
        if s.startswith("_") or "version" in s.lower():
            continue
        val = getattr(Settings, s)
        if isinstance(val, (Path, VersionInfo)):
            val = str(val)
        ret[s] = val
    return ret


def load_settings(to_load: Dict[str, Any]) -> None:
    """
    Sets the Settings from a dict. Environment variables are respected and have
    higher priority
    """
    for s in to_load:
        if s in _ENV_VAR_SETTINGS:
            env_var = _ENV_VAR_SETTINGS[s]()
            if env_var:
                setattr(Settings, s, env_var)
                continue
        setattr(Settings, s, to_load[s])
    # Restore proper types
    Settings.DATA_DIR = Path(Settings.DATA_DIR)
    Settings.SIM_MODE = SimMode(Settings.SIM_MODE)
    Settings.SIM_TYPE = SimType(Settings.SIM_TYPE)


def _port_env_var(env_var: str, default: Optional[int] = None) -> int:
    var = os.getenv(env_var)
    return int(var) if var else default


def _bb_logs_root_env_var(default: Optional[Path] = None) -> Path:
    var = os.getenv("BB_LOGS_ROOT")
    return Path(var) if var else default


_ENV_VAR_SETTINGS = {
    "BB_PORT": functools.partial(_port_env_var, "BB_PORT"),
    "BB_LOGS_ROOT": _bb_logs_root_env_var,
    "BS_EVENT_PORT": functools.partial(_port_env_var, "BS_EVENT_PORT"),
    "BS_STREAM_PORT": functools.partial(_port_env_var, "BS_STREAM_PORT"),
}


class Settings:
    """
    BlueBird's settings.

    Attributes:
        VERSION:            BlueBird release version
        API_VERSION:        BlueBird API version
        FLASK_DEBUG:        FLASK_DEBUG flag for `Flask.run(debug=FLASK_DEBUG)`
        BB_PORT:               BlueBird (Flask) server port
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
    BB_PORT: int = _ENV_VAR_SETTINGS["BB_PORT"](5001)

    DATA_DIR = Path("data")

    SIM_LOG_RATE: float = 0.2
    LOGS_ROOT: Path = _ENV_VAR_SETTINGS["BB_LOGS_ROOT"](Path("logs"))
    CONSOLE_LOG_LEVEL: int = logging.DEBUG

    SIM_HOST: str = "localhost"
    SIM_MODE: SimMode = SimMode.Agent
    SIM_TYPE: SimType = SimType.BlueSky

    # BlueSky settings
    BS_EVENT_PORT: int = _ENV_VAR_SETTINGS["BS_EVENT_PORT"](9000)
    BS_STREAM_PORT: int = _ENV_VAR_SETTINGS["BS_STREAM_PORT"](9001)
    BS_STREAM_TIMEOUT: int = 5
    BS_TIMEOUT: int = 10

    # MachColl settings
    MC_PORT: int = 5321
