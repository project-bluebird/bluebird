"""
MachColl simulation client class
"""

import logging
import os
from typing import Iterable, Union, Optional

from semver import VersionInfo

from bluebird.settings import Settings
from bluebird.sim_client.abstract_sim_client import (
    AbstractAircraftControls,
    AbstractSimulatorControls,
    AbstractWaypointControls,
    AbstractSimClient,
)
from bluebird.utils.types import Callsign, LatLon, Altitude, Heading

# TODO Import this from top-level / add setup instructions
from .interface.mc_client import MCClient

_LOGGER = logging.getLogger(__name__)

_MC_MIN_VERSION = os.getenv("MC_MIN_VERSION")
if not _MC_MIN_VERSION:
    raise ValueError("The MC_MIN_VERSION environment variable must be set")

MIN_SIM_VERSION = VersionInfo.parse(_MC_MIN_VERSION)


class MachCollAircraftControls(AbstractAircraftControls):
    """
    AbstractAircraftControls implementation for MachColl
    """

    def __init__(self, client: MCClient):
        self._client = client

    def set_cleared_fl(
        self, callsign: Callsign, flight_level: Altitude, **kwargs
    ) -> Optional[str]:
        raise NotImplementedError

    def add_waypoint_to_route(
        self, callsign: Callsign, target: Union[str, LatLon], **kwargs
    ) -> Optional[str]:
        raise NotImplementedError

    def create(
        self,
        callsign: Callsign,
        ac_type: str,
        position: LatLon,
        heading: Heading,
        altitude: Altitude,
        speed: int,
    ) -> Optional[str]:
        raise NotImplementedError

    def get_properties(self, callsign: Optional[Callsign]) -> str:
        """
        Get all the properties for an aircraft
        :param callsign:
        """
        raise NotImplementedError


class MachCollSimulatorControls(AbstractSimulatorControls):
    """
    
    """

    @property
    def sim_state(self) -> str:
        raise NotImplementedError

    def __init__(self, client: MCClient):
        self._client = client

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        raise NotImplementedError

    def start(self) -> Optional[str]:
        raise NotImplementedError

    def reset(self) -> Optional[str]:
        raise NotImplementedError

    def pause(self) -> Optional[str]:
        raise NotImplementedError

    def resume(self) -> Optional[str]:
        raise NotImplementedError

    def step(self) -> Optional[str]:
        raise NotImplementedError

    def get_speed(self) -> float:
        raise NotImplementedError

    def set_speed(self, speed) -> Optional[str]:
        raise NotImplementedError

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def get_seed(self) -> int:
        raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        raise NotImplementedError

    def get_time(self) -> Optional[str]:
        raise NotImplementedError


class MachCollWaypointControls(AbstractWaypointControls):
    """   
    
    """

    def __init__(self, client: MCClient):
        self._client = client

    def define(self, name: str, position: LatLon, **kwargs) -> Optional[str]:
        raise NotImplementedError


class SimClient(AbstractSimClient):
    """
    AbstractSimClient implementation for MachColl
    """

    @property
    def sim_version(self) -> VersionInfo:
        return self._host_version

    @property
    def simulator(self) -> AbstractSimulatorControls:
        return self._sim_controls

    @property
    def aircraft(self) -> AbstractAircraftControls:
        return self._aircraft_controls

    @property
    def waypoints(self) -> AbstractWaypointControls:
        return self._waypoint_controls

    def __init__(self, **kwargs):
        self._client = None
        self._host_version: VersionInfo = None
        self._sim_controls = MachCollSimulatorControls(self._client)
        self._aircraft_controls = MachCollAircraftControls(self._client)
        self._waypoint_controls = MachCollWaypointControls(self._client)

    def connect(self, timeout: int = 1) -> None:
        self._client = MCClient(host=Settings.SIM_HOST, port=Settings.MC_PORT)

        # Perform a request to initialise the connection
        if not self._client.get_state():
            raise TimeoutError("Could not connect to the MachColl server")

        # TODO Get and handle the other versions (server, database, ?)
        # TODO Properly handle the "x.x" version string
        version_dict = self._client.compare_api_version()
        self._host_version = VersionInfo.parse(
            version_dict["This client version"] + ".0"
        )

    def start_timers(self):
        return []

    def stop(self, shutdown_sim: bool = False):

        if not self._host_version:
            return

        resp = self._client.sim_stop()
        _LOGGER.warning(f"stop(): Received response from MCClient - {resp}")
