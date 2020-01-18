"""
Contains the BlueBird class
"""
import logging
import os
import signal
import threading
import time
import traceback
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from semver import VersionInfo

from bluebird.api import FLASK_APP
from bluebird.api.resources.utils.utils import FLASK_CONFIG_LABEL
from bluebird.metrics import setup_metrics
from bluebird.settings import Settings
from bluebird.sim_client import setup_sim_client
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.utils.abstract_sim_client import AbstractSimClient


class BlueBird:
    """The BlueBird application"""

    exit_flag: bool = False

    def __init__(self, args: Dict[str, Any]):

        self._logger = logging.getLogger(__name__)
        self._logger.info(
            f"BlueBird init - sim type: {Settings.SIM_TYPE.name}, "
            f"mode: {Settings.SIM_MODE.name}"
        )

        self._cli_args = args
        self._min_sim_version: Optional[VersionInfo] = None
        self._timers: List = []

        self.sim_proxy: Optional[SimProxy] = None
        self.sim_client: Optional[AbstractSimClient] = None

        self.metrics_providers = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stops the app and cleans up any threaded code"""

        self._logger.info("BlueBird stopping")

        for timer in self._timers:
            timer.stop()

        if self.sim_proxy:
            self.sim_proxy.shutdown()

        BlueBird.exit_flag = True

    def pre_connection_setup(self):
        """Performs any actions required before connecting to the simulator"""

        self.metrics_providers = setup_metrics()

        # NOTE(RKM 2019-12-12) The sim clients get a reference to the metrics providers
        # so they can store any results there if needed (i.e. storing the result of all
        # metrics after a call to step)
        self.sim_client, self._min_sim_version = setup_sim_client(
            self.metrics_providers
        )

        self.sim_proxy = SimProxy(self.sim_client, self.metrics_providers)

    def connect_to_sim(self) -> bool:
        """
        Connect to the simulation server
        :param args: Parsed CLI arguments
        :return: True if a connection was established with the server, otherwise False
        """

        sim_name = Settings.SIM_TYPE.name
        self._logger.info(f"Attempting to connect to {sim_name} at {Settings.SIM_HOST}")

        try:
            self.sim_proxy.connect()
        except (TimeoutError, KeyboardInterrupt):
            self._logger.error(
                f"Failed to connect to {sim_name}, exiting ({traceback.format_exc()})"
            )
            return False

        self._logger.info("Client connected")

        if self.sim_proxy.sim_version < self._min_sim_version:
            self._logger.error(
                f"Server of version {self.sim_proxy.sim_version} does not meet the "
                f"minimum requirement ({self._min_sim_version})"
            )
            return False

        if self.sim_proxy.sim_version.major > self._min_sim_version.major:
            self._logger.error(
                f"{sim_name} server of version {self.sim_proxy.sim_version} has major"
                f"version greater than supported in this version of the client"
                f"({self._min_sim_version})"
            )
            return False

        self._timers.extend(self.sim_proxy.start_timers())

        # NOTE(rkm 2020-01-09) This has to be done after we start the timers since,
        # for BlueSky at least, we need to actively poll for the reset confirmation
        if self._cli_args["reset_sim"]:
            err = self.sim_proxy.simulation.reset()
            if err:
                raise RuntimeError(f"Could not reset sim on startup: {err}")

        self.sim_proxy.pre_fetch_data()

        return True

    def run(self):
        """
        Start the Flask app. This is a blocking method which only returns once the app
        exists
        """

        self._logger.debug(
            f"Starting BlueBird API v{Settings.API_VERSION} on "
            f"0.0.0.0:{Settings.PORT}"
        )

        # Register the BlueBird app with Flask so the API thread can use it
        FLASK_APP.config[FLASK_CONFIG_LABEL] = self

        flask_thread = threading.Thread(
            target=FLASK_APP.run,
            kwargs={
                "host": "0.0.0.0",
                "port": Settings.PORT,
                "debug": Settings.FLASK_DEBUG,
                "use_reloader": False,
            },
        )

        flask_thread.start()

        try:
            while flask_thread.isAlive() and not self._check_timers():
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._logger.info("Ctrl+C - exiting")
            _proc_killer()
            return

        err = self._check_timers()
        if err:
            exc_type, exc_value, exc_traceback = err
            _proc_killer()
            raise exc_type(exc_value).with_traceback(exc_traceback)

    def _check_timers(self):
        """
        Checks if any threads have raised an exception. Returns the first found
        exception, or None
        """
        return next((x.exc_info for x in self._timers if x.exc_info), None)


def _proc_killer():
    r"""
    Starts another thread which waits for BlueBird.exit_flag to be set, then sends
    SIGINT to our own process. This is apparently the easiest way to clean things up and
    cause the Flask server to exit if you decide to run it in another thread ¯\_(ツ)_/¯
    """

    def killer():
        while not BlueBird.exit_flag:
            time.sleep(0.1)
        os.kill(os.getpid(), signal.SIGINT)

    threading.Thread(target=killer).start()
