"""
Contains the BlueBird class
"""

import logging

from bluebird.settings import Settings
from bluebird.api import FLASK_APP
from bluebird.api.resources.utils import FLASK_CONFIG_LABEL
from bluebird.cache.acdatacache import AcDataCache
from bluebird.cache.sim_state import SimState
from bluebird.metrics import setup_metrics
from bluebird.sim_client import setup_sim_client


class BlueBird:
    """
    The BlueBird application
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.info(
            f"BlueBird init - sim type: {Settings.SIM_TYPE.name}, "
            f"mode: {Settings.SIM_MODE.name}"
        )

        # TODO Refactor these two into a single Simulation proxy class
        self.sim_state = SimState()
        self.ac_data = AcDataCache(self.sim_state)

        self.sim_client = None
        self._min_sim_version = None
        self._timers = []
        self.metrics_providers = setup_metrics(self.ac_data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stops the app and cleans up any threaded code
        """

        self._logger.info("BlueBird stopping")

        for timer in self._timers:
            timer.stop()

        if self.sim_client:
            self.sim_client.stop()

    def setup_sim_client(self):
        """
        Setup the simulation client class
        :return:
        """

        self.sim_client, self._min_sim_version = setup_sim_client(
            self.sim_state, self.ac_data
        )
        self._timers.extend(self.sim_client.start_timers())

    def connect_to_sim(self, reset_on_connect: bool):
        """
        Connect to the simulation server
        :return: True if a connection was established with the server, otherwise false
        """

        self._logger.info("Connecting to client...")

        try:
            self.sim_client.connect()
        except TimeoutError:
            self._logger.error(
                f"Failed to connect to {Settings.SIM_TYPE.name} server at "
                f"{Settings.SIM_HOST}, exiting"
            )
            self.sim_client.stop()
            return False

        if self.sim_client.host_version < self._min_sim_version:
            self._logger.error(
                f"BlueSky server of version {self.sim_client.host_version} does not meet the "
                f"minimum requirement ({self._min_sim_version})"
            )
            return False

        if self.sim_client.host_version.major > self._min_sim_version.major:
            self._logger.error(
                f"BlueSky server of version {self.sim_client.host_version} has major version "
                f"greater than supported in this version of client ({self._min_sim_version})"
            )
            return False

        if reset_on_connect:
            self.sim_client.reset_sim()

        self._timers.append(self.sim_state.start_timer())
        return True

    def run(self):
        """
        Start the Flask app. This is a blocking method which only returns once the app exists.
        """

        self._logger.debug("Starting Flask app")

        # TODO This should be in connect_to_sim?
        self._timers.append(self.ac_data.start_timer())
        FLASK_APP.config[FLASK_CONFIG_LABEL] = self
        FLASK_APP.run(
            host="0.0.0.0",
            port=Settings.PORT,
            debug=Settings.FLASK_DEBUG,
            use_reloader=False,
        )
