"""
MachColl simulation client class

NOTE: The allowed state transitions appear to be -
Init        -> Running, Stepping
Running     -> Paused, Stopped
Stopped     -> Running, Stepping
Paused      -> Running, Stepping, Stopped
Stepping    -> Paused, Stopped
"""

import logging
import os
from typing import Iterable

from semver import VersionInfo

from .machcoll_client_imports import MCClientMetrics
from .machcoll_aircraft_controls import MachCollAircraftControls
from .machcoll_simulator_controls import MachCollSimulatorControls
from .machcoll_waypoint_controls import MachCollWaypointControls
from bluebird.metrics import MetricsProviders
from bluebird.settings import Settings
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.utils.timer import Timer


_MC_MIN_VERSION = os.getenv("MC_MIN_VERSION")
if not _MC_MIN_VERSION:
    raise ValueError("The MC_MIN_VERSION environment variable must be set")

MIN_SIM_VERSION = VersionInfo.parse(_MC_MIN_VERSION)


def _raise_for_no_data(data):
    assert data, "No data received from the simulator"


class SimClient(AbstractSimClient):
    """
    AbstractSimClient implementation for MachColl
    """

    @property
    def aircraft(self) -> MachCollAircraftControls:
        return self._aircraft_controls

    @property
    def simulation(self) -> MachCollSimulatorControls:
        return self._sim_controls

    @property
    def sim_version(self) -> VersionInfo:
        return self._client_version

    @property
    def waypoints(self) -> MachCollWaypointControls:
        return self._waypoint_controls

    def __init__(self, metrics_providers: MetricsProviders):
        self.mc_client = None
        self._client_version: VersionInfo = None
        self._logger = logging.getLogger(__name__)
        self._aircraft_controls = MachCollAircraftControls(self)
        self._mc_metrics_provider = metrics_providers.get("MachColl")
        self._sim_controls = MachCollSimulatorControls(
            self, self._aircraft_controls, self._mc_metrics_provider,
        )
        self._waypoint_controls = MachCollWaypointControls(self)

    def connect(self, timeout: int = 1) -> None:
        self.mc_client = MCClientMetrics(host=Settings.SIM_HOST, port=Settings.MC_PORT)

        # Perform a request to initialise the connection
        if not self.mc_client.get_state():
            raise TimeoutError("Could not connect to the MachColl server")

        version_dict = self.mc_client.compare_api_version()
        self._client_version = VersionInfo.parse(version_dict["This client version"])
        self._mc_metrics_provider.set_version(self._client_version)
        self._logger.info(f"MCClientMetrics connected. Version: {self._client_version}")

    def start_timers(self) -> Iterable[Timer]:
        # NOTE(RKM 2019-11-18) MCClientMetrics is passive for now - we don't have any
        # stream data
        return []

    def shutdown(self, shutdown_sim: bool = False) -> bool:

        if self.mc_client:
            self.mc_client.close_mq()

        # NOTE: Using the presence of _client_version to infer that we have a connection
        if not self._client_version:
            return True

        # TODO(RKM 2019-11-24) Re-enable this once the sandbox mode is fixed
        # sim_props = self.simulation.properties
        # if isinstance(sim_props, str):
        #     self._logger.error(
        #         f"Could not pause sim while disconnecting:\n'{sim_props}'"
        #     )
        # elif sim_props.state == props.SimState.RUN:
        #     stop_str = self.simulation.pause()
        #     shutdown_ok = True
        #     if stop_str:
        #         self._logger.error(f"Error when stopping simulation: {stop_str}")
        #         shutdown_ok = False

        if not shutdown_sim:
            return True

        self._logger.warning("No sim shutdown method implemented")
        # return shutdown_ok
        return True
