"""Contains the class which implements episode (scenario) logging"""
import logging
import uuid

from bluebird.settings import Settings
from bluebird.settings import time_for_logfile
from bluebird.utils.properties import SimProperties


_ACT_LOG_PREFIX = "A"
_CMD_LOG_PREFIX = "C"
_EVT_LOG_PREFIX = "E"


class EpisodeLogger:
    """Class which implements episode (scenario) logging"""

    def __init__(self):
        self._episode_id = None
        self._episode_file = None
        self._logger = logging.getLogger("episode")
        self._proxy_sim_controls = None

    def set_proxy_sim_controls(self, proxy_sim_controls):
        self._proxy_sim_controls = proxy_sim_controls

    def close_episode_log(self, reason):
        """Closes the currently open episode log, if there is one"""
        if not self._logger.hasHandlers():
            return
        self._logger.info(
            f"Episode finished ({reason})", extra={"PREFIX": _EVT_LOG_PREFIX}
        )
        self._logger.handlers[-1].close()
        self._logger.handlers.pop()

    def restart_episode_log(self, sim_props: SimProperties):
        """
        Closes the current episode log and starts a new one. Returns the UUID of the new
        episode
        """
        self.close_episode_log("episode logging restarted")
        return self._start_episode_log(sim_props)

    def log_command(self, command: str):
        props = self._proxy_sim_controls.properties
        assert isinstance(props, SimProperties)
        self._logger.info(
            f"[{props.scenario_time}] {command}", extra={"PREFIX": _CMD_LOG_PREFIX}
        )

    def _start_episode_log(self, sim_props: SimProperties):
        """Starts a new episode logfile"""

        if self._logger.hasHandlers():
            raise Exception(
                f"Episode logger already has a handler assigned: "
                f"{self._logger.handlers}"
            )

        EP_ID = uuid.uuid4()
        assert Settings.INST_LOG_DIR
        EP_FILE = Settings.INST_LOG_DIR / f"{time_for_logfile()}_{EP_ID}.log"
        file_handler = logging.FileHandler(EP_FILE)
        file_handler.name = "episode-file"
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s %(PREFIX)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        # self._logger.info(
        #     f"Episode started. Seed is {sim_seed}", extra={"PREFIX": _EVT_LOG_PREFIX},
        # )

        return EP_ID
