"""
Logging configuration for BlueBird
"""
# TODO(rkm 2020-01-12) Refactor the episode logging code into SimProxy
import json
import logging.config
import uuid
from datetime import datetime
from pathlib import Path

from bluebird.settings import Settings


if not Settings.LOGS_ROOT.exists():
    Settings.LOGS_ROOT.mkdir()


def time_for_logfile():
    """Returns the current timestamp formatted for a logfile name"""
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


INSTANCE_ID = uuid.uuid1()
INST_LOG_DIR = Path(Settings.LOGS_ROOT, f"{time_for_logfile()}_{INSTANCE_ID}")
INST_LOG_DIR.mkdir()

with open("bluebird/logging_config.json") as f:
    LOG_CONFIG = json.load(f)
    LOG_CONFIG["handlers"]["console"]["level"] = Settings.CONSOLE_LOG_LEVEL

# Set filenames for logfiles (can't do this from the JSON)
LOG_CONFIG["handlers"]["debug-file"]["filename"] = INST_LOG_DIR / "debug.log"

# Set the logging config
logging.config.dictConfig(LOG_CONFIG)

_LOGGER = logging.getLogger("bluebird")

# Setup episode logging

EP_ID = EP_FILE = None
EP_LOGGER = logging.getLogger("episode")
EP_LOGGER.setLevel(logging.DEBUG)

_LOG_PREFIX = "E"


def close_episode_log(reason):
    """Closes the currently open episode log, if there is one"""

    if not EP_LOGGER.hasHandlers():
        return

    EP_LOGGER.info(f"Episode finished ({reason})", extra={"PREFIX": _LOG_PREFIX})
    EP_LOGGER.handlers[-1].close()
    EP_LOGGER.handlers.pop()


def _start_episode_log(sim_seed):
    """Starts a new episode logfile"""

    global EP_ID, EP_FILE

    if EP_LOGGER.hasHandlers():
        raise Exception(
            f"Episode logger already has a handler assigned: {EP_LOGGER.handlers}"
        )

    EP_ID = uuid.uuid4()
    EP_FILE = INST_LOG_DIR / f"{time_for_logfile()}_{EP_ID}.log"
    file_handler = logging.FileHandler(EP_FILE)
    file_handler.name = "episode-file"
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s %(PREFIX)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    EP_LOGGER.addHandler(file_handler)
    EP_LOGGER.info(
        f"Episode started. SIM_LOG_RATE is {Settings.SIM_LOG_RATE} Hz. "
        f"Seed is {sim_seed}",
        extra={"PREFIX": _LOG_PREFIX},
    )

    return EP_ID


def restart_episode_log(sim_seed):
    """
    Closes the current episode log and starts a new one. Returns the UUID of the new
    episode
    """

    close_episode_log("episode logging restarted")
    return _start_episode_log(sim_seed)
