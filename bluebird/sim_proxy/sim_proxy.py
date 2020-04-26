"""
Contains the SimProxy class
"""
# TODO(RKM 2019-11-17) With the current SimProxy implementation, we assume that we are
# the only client interacting with the simulation server when taking any actions that
# involve updating the scenario / creating waypoints etc. This might cause trouble if
# we wish to run another demo which involves multiple instances of BlueBird interacting
# with the same simulation. If we want to support that, then we'll have to add logic
# which allows one of the instances to act as the "master", and make the other instances
# aware that some properties may change without their knowledge
import logging
from typing import List

from semver import VersionInfo

from bluebird.metrics import MetricsProviders
from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.utils.timer import Timer


class SimProxy(AbstractSimClient):
    """
    Class which intercepts any requests before forwarding them to the sim client. Allows
    any actions to be taken which are independent of the particular sim client
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

    def __init__(
        self, sim_client: AbstractSimClient, metrics_providers: MetricsProviders
    ):
        self._logger = logging.getLogger(__name__)

        # The actual sim_client
        self._sim_client: AbstractSimClient = sim_client

        # The proxy implementations
        self._proxy_aircraft_controls = ProxyAircraftControls(self._sim_client.aircraft)
        self._proxy_simulator_controls = ProxySimulatorControls(
            self._sim_client.simulation, self._proxy_aircraft_controls
        )

        self.metrics_providers = metrics_providers

    def connect(self, timeout: int = 1) -> None:
        self._sim_client.connect(timeout)

    def start_timers(self) -> List[Timer]:
        return [
            *self._sim_client.start_timers(),
            *self._proxy_simulator_controls.start_timers(),
        ]

    def pre_fetch_data(self):
        """Called on startup to fetch the initial state"""
        _ = self._sim_client.aircraft.all_properties
        _ = self._sim_client.simulation.properties

    def shutdown(self, shutdown_sim: bool = False) -> bool:
        """
        Shutdown the sim client
        :param shutdown_sim: If true, and if the simulation server supports it, will
        also send a shutdown command
        :return: If shutdown_sim was requested, the return value will indicate whether
        the simulator was shut down successfully. Always returns True if shutdown_sim
        was not requested
        """
        err = self._proxy_simulator_controls.store_data()
        if err:
            self._logger.error(err)
        return self._sim_client.shutdown(shutdown_sim)

    def call_metric_function(
        self, provider: AbstractMetricsProvider, metric_name: str, args: list
    ):
        """Calls the metric specified"""
        # NOTE(rkm 2020-01-12) We pass the aircraft and simulator control objects to any
        # metric which is called so that it can have access to any property it needs
        return provider(
            metric_name,
            *args,
            aircraft_controls=self._proxy_aircraft_controls,
            simulator_controls=self._proxy_simulator_controls
        )
