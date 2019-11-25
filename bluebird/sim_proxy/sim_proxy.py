"""
Contains the SimProxy class
"""

# TODO(RKM 2019-11-17) Add functionality which never relies on any cached values. This
# may be useful in cases where we are expecting multiple clients to be interacting with
# the same simulation

import logging
from typing import Iterable

from semver import VersionInfo

from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls
from bluebird.sim_proxy.proxy_waypoint_controls import ProxyWaypointControls
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.utils.timer import Timer


class SimProxy(AbstractSimClient):
    """
    Class for handling and routing requests to the simulator client
    """

    @property
    def aircraft(self) -> ProxyAircraftControls:
        return self._proxy_aircraft_controls

    @property
    def simulation(self) -> ProxySimulatorControls:
        return self._proxy_simulator_controls

    @property
    def sim_version(self) -> VersionInfo:
        return self._sim_client.sim_version

    @property
    def waypoints(self) -> ProxyWaypointControls:
        return self._proxy_waypoint_controls

    def __init__(self, sim_client: AbstractSimClient):

        self._logger = logging.getLogger(__name__)

        # The actual sim_client
        self._sim_client: AbstractSimClient = sim_client

        # The proxy implementations
        self._proxy_aircraft_controls = ProxyAircraftControls(self._sim_client.aircraft)
        self._proxy_waypoint_controls = ProxyWaypointControls(
            self._sim_client.waypoints
        )
        self._proxy_simulator_controls = ProxySimulatorControls(
            self._sim_client.simulation,
            self._proxy_aircraft_controls,
            self._proxy_waypoint_controls,
        )

    def connect(self, timeout: int = 1) -> None:
        self._sim_client.connect(timeout)

    def start_timers(self) -> Iterable[Timer]:
        # TODO(RKM 2019-11-18) Start own timers
        return self._sim_client.start_timers()

    def pre_fetch_data(self):
        _ = self._sim_client.aircraft.all_properties
        _ = self._sim_client.simulation.properties
        self.waypoints

    def shutdown(self, shutdown_sim: bool = False) -> bool:
        """
        Shutdown the sim client
        :param shutdown_sim: If true, and if the simulation server supports it, will
        also send a shutdown command
        :return: If shutdown_sim was requested, the return value will indicate whether
        the simulator was shut down successfully. Always returns True if shutdown_sim
        was not requested
        """
        return self._sim_client.shutdown(shutdown_sim)
