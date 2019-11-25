"""
Contains the BlueBird class
"""

import logging
import traceback
from typing import Any, Dict, Optional

from bluebird.api import FLASK_APP
from bluebird.api.resources.utils.utils import FLASK_CONFIG_LABEL
from bluebird.metrics import setup_metrics
from bluebird.settings import Settings
from bluebird.sim_client import setup_sim_client
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.sim_proxy.sim_proxy import SimProxy


class BlueBird:
    """
    The BlueBird application
    """

    def __init__(self, args: Dict[str, Any]):

        self._logger = logging.getLogger(__name__)
        self._logger.info(
            f"BlueBird init - sim type: {Settings.SIM_TYPE.name}, "
            f"mode: {Settings.SIM_MODE.name}"
        )

        self._cli_args = args
        self._min_sim_version = None
        self._timers = []

        self.sim_proxy: Optional[SimProxy] = None
        self.sim_client: Optional[AbstractSimClient] = None

        self.metrics_providers = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stops the app and cleans up any threaded code
        """

        self._logger.info("BlueBird stopping")

        for timer in self._timers:
            timer.stop()

        if self.sim_proxy:
            self.sim_proxy.shutdown()

    def setup_sim_client(self):
        """
        Setup the simulation client class
        :return:
        """

        self.metrics_providers = setup_metrics()
        self.sim_client, self._min_sim_version = setup_sim_client(
            self.metrics_providers
        )
        self.sim_proxy = SimProxy(self.sim_client)

    def connect_to_sim(self):
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

        if self.sim_proxy.sim_version < self._min_sim_version:
            self._logger.error(
                f"server of version {self.sim_proxy.sim_version} does not meet the "
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

        if self._cli_args["reset_sim"]:
            err = self.sim_proxy.simulation.reset()
            if err:
                raise RuntimeError(f"Could not reset sim on startup: {err}")

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

        FLASK_APP.config[FLASK_CONFIG_LABEL] = self

        FLASK_APP.run(
            host="0.0.0.0",
            port=Settings.PORT,
            debug=Settings.FLASK_DEBUG,
            use_reloader=False,
        )
