"""
Contains the BlueBird class
"""

import logging
from typing import Any, Dict

from bluebird.api import FLASK_APP
from bluebird.api.resources.utils.utils import FLASK_CONFIG_LABEL
from bluebird.metrics import setup_metrics
from bluebird.settings import Settings
from bluebird.sim_client import setup_sim_client
from bluebird.sim_proxy.sim_proxy import SimProxy


class BlueBird:
    """
    The BlueBird application
    """

    def __init__(self, args: Dict[str, Any]):

        self._logger = logging.getLogger(__name__)
        self._logger.info(
            f"BlueBird init - sim type: {Settings.SIM_TYPE.name}, "
            f"mode: {Settings.SIM_MODE.name}, streaming: {Settings.STREAM_ENABLE}"
        )

        self._cli_args = args
        self._sim_client = None
        self._min_sim_version = None
        self._metrics_providers = None
        self._timers = []

        self.sim_proxy = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stops the app and cleans up any threaded code
        """

        self._logger.info("BlueBird stopping")

        for timer in self._timers:
            timer.stop()

        if self._sim_client:
            self._sim_client.stop()

    def setup_sim_client(self):
        """
        Setup the simulation client class
        :return:
        """

        self._sim_client, self._min_sim_version = setup_sim_client()
        self.sim_proxy = SimProxy(self._sim_client)
        self._metrics_providers = setup_metrics()

        # TODO What to do here?
        self._timers.extend(self._sim_client.start_timers())

    def connect_to_sim(self):
        """
        Connect to the simulation server
        :param args: Parsed CLI arguments
        :return: True if a connection was established with the server, otherwise False
        """

        sim_name = Settings.SIM_TYPE.name
        self._logger.info(f"Attempting to connect to {sim_name} at {Settings.SIM_HOST}")

        try:
            self._sim_client.connect()
        except TimeoutError:
            self._logger.error(f"Failed to connect to {sim_name}, exiting")
            return False

        if self._sim_client.sim_version < self._min_sim_version:
            self._logger.error(
                f"server of version {self._sim_client.sim_version} does not meet the "
                f"minimum requirement ({self._min_sim_version})"
            )
            return False

        if self._sim_client.sim_version.major > self._min_sim_version.major:
            self._logger.error(
                f"{sim_name} server of version {self._sim_client.sim_version} has major"
                f"version greater than supported in this version of the client"
                f"({self._min_sim_version})"
            )
            return False

        # TODO: We may want to pre-fetch the list of available aircraft types here

        if self._cli_args["reset_sim"]:
            self._sim_client.reset_sim()

        # self._timers.extend([self.sim_state.start_timer(), self.ac_data.start_timer()])

        return True

    def run(self):
        """
        Start the Flask app. This is a blocking method which only returns once the app
        exists
        """

        self._logger.debug("Starting Flask app")

        FLASK_APP.config[FLASK_CONFIG_LABEL] = self
        FLASK_APP.run(
            host="0.0.0.0",
            port=Settings.PORT,
            debug=Settings.FLASK_DEBUG,
            use_reloader=False,
        )
