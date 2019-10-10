"""
MachColl simulation client class
"""

import logging
import os
from typing import Iterable, Optional, List, Union

from semver import VersionInfo

from bluebird.settings import is_agent_mode, Settings
from bluebird.sim_client.abstract_sim_client import (
    AbstractAircraftControls,
    AbstractSimulatorControls,
    AbstractWaypointControls,
    AbstractSimClient,
)
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties, SimProperties
from bluebird.utils.timer import Timer

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

    @property
    def stream_data(self) -> List[AircraftProperties]:
        raise NotImplementedError

    def __init__(self, client):
        self._client = client

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        err = self._client.set_cfl(callsign, flight_level.flight_levels)
        return str(err) if err else None

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        raise NotImplementedError

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        raise NotImplementedError

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        raise NotImplementedError

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        raise NotImplementedError

    def add_waypoint_to_route(
        self, callsign: types.Callsign, waypoint: types.Waypoint, **kwargs
    ) -> Optional[str]:
        raise NotImplementedError

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        speed: int,
    ) -> Optional[str]:
        raise NotImplementedError

    def get_properties(self, callsign: types.Callsign) -> Optional[AircraftProperties]:
        raise NotImplementedError

    def get_all_properties(self) -> List[AircraftProperties]:
        raise NotImplementedError


class MachCollSimulatorControls(AbstractSimulatorControls):
    """
    AbstractSimulatorControls implementation for MachColl
    """

    @property
    def stream_data(self) -> SimProperties:
        raise NotImplementedError

    @property
    def properties(self) -> Union[SimProperties, str]:
        raise NotImplementedError

    def __init__(self, client):
        self._client = client

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        raise NotImplementedError

    def start(self) -> Optional[str]:
        resp = self._client.sim_start()
        if not resp:
            return "Could not connect to sim"
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def reset(self) -> Optional[str]:
        resp = self._client.sim_stop()
        if not resp:
            return "Could not connect to sim"
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def pause(self) -> Optional[str]:
        resp = self._client.sim_pause()
        if not resp:
            return "Could not connect to sim"
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def resume(self) -> Optional[str]:
        resp = self._client.sim_resume()
        if not resp:
            return "Could not connect to sim"
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def step(self) -> Optional[str]:
        resp = self._client.set_increment()
        if not resp:
            return "Could not connect to sim"
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def get_speed(self) -> float:
        resp = self._client.get_step() if is_agent_mode() else self._client.get_speed()
        if not resp:
            raise RuntimeError("Could not connect to sim")
        _LOGGER.warning(f"Unhandled data: {resp}")
        return -1

    def set_speed(self, speed: float) -> Optional[str]:
        resp = (
            self._client.set_step(speed)
            if is_agent_mode()
            else self._client.set_speed(speed)
        )
        if not resp:
            raise RuntimeError("Could not connect to sim")
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def get_seed(self) -> int:
        raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        # NOTE: There is a function in McClient for this, but it isn't implemented there
        # yet
        raise NotImplementedError


class MachCollWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for MachColl
    """

    def __init__(self, client):
        self._client = client

    def get_all_waypoints(self) -> dict:
        fixes = self._client.get_all_fixes()
        if not isinstance(fixes, dict):
            raise NotImplementedError(f"get_all_fixes returned: {fixes}")
        # TODO Need to create a mapping
        _LOGGER.warning(f"Unhandled data: {fixes}")
        return {}

    def define(self, name: str, position: types.LatLon, **kwargs) -> Optional[str]:
        raise NotImplementedError


class SimClient(AbstractSimClient):
    """
    AbstractSimClient implementation for MachColl
    """

    @property
    def aircraft(self) -> AbstractAircraftControls:
        return self._aircraft_controls

    @property
    def simulation(self) -> AbstractSimulatorControls:
        return self._sim_controls

    @property
    def sim_version(self) -> VersionInfo:
        return self._host_version

    @property
    def waypoints(self) -> AbstractWaypointControls:
        return self._waypoint_controls

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
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

    def start_timers(self) -> Iterable[Timer]:
        return []

    def stop(self, shutdown_sim: bool = False) -> bool:

        if not self._host_version or not shutdown_sim:
            return True

        raise NotImplementedError("No sim shutdown method implemented")
