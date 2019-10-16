"""
BlueSky simulation client class
"""

import logging
import os
from typing import Optional, Iterable, List, Union, Dict

from semver import VersionInfo

from bluebird.settings import Settings
from bluebird.sim_client.abstract_sim_client import (
    AbstractAircraftControls,
    AbstractSimulatorControls,
    AbstractWaypointControls,
    AbstractSimClient,
)
from bluebird.sim_client.bluesky.bluesky_client import BlueSkyClient
from bluebird.utils.properties import AircraftProperties, SimProperties
from bluebird.utils.timer import Timer
import bluebird.utils.types as types


_LOGGER = logging.getLogger(__name__)

_BS_MIN_VERSION = os.getenv("BS_MIN_VERSION")
if not _BS_MIN_VERSION:
    raise ValueError("The BS_MIN_VERSION environment variable must be set")

MIN_SIM_VERSION = VersionInfo.parse(_BS_MIN_VERSION)


# TODO Check cases where we need this
def _assert_valid_args(args: list):
    """
    Since BlueSky only accepts commands in the form of (variable-length) strings, we
    need to check the arguments for each command string we construct before sending it
    """

    # Probably a cleaner way of doing this...
    assert all(
        x and not x.isspace() and x != "None" for x in map(str, args)
    ), f"Invalid argument in : {args}"


class BlueSkyAircraftControls(AbstractAircraftControls):
    """
    AbstractAircraftControls implementation for BlueSky
    """

    @property
    def stream_data(self) -> List[AircraftProperties]:
        return self._client.aircraft_stream_data

    def __init__(self, client):
        self._client = client

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:

        vspd = kwargs.get("vspd", "")
        cmd_str = f"ALT {callsign} {flight_level} {vspd}".strip()
        # TODO This can also return list (multiple errors?)
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        cmd_str = f"HDG {callsign} {heading}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        cmd_str = f"SPD {callsign} {ground_speed}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        cmd_str = f"VS {callsign} {vertical_speed}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        cmd_str = f"DIRECT {callsign} {waypoint}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    # TODO Check how BlueSky handles the variable length arguments here with LAT LON
    def add_waypoint_to_route(
        self, callsign: types.Callsign, waypoint: types.Waypoint, **kwargs
    ) -> Optional[str]:
        cmd_str = f"ADDWPT {callsign} {waypoint}"
        cmd_str += " " + kwargs.get("alt", "")
        cmd_str += " " + kwargs.get("spd", "")
        cmd_str.strip()
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        speed: int,
    ) -> Optional[str]:
        cmd_str = f"CRE {callsign} {ac_type} {position} {heading} {altitude} {speed}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def get_properties(self, callsign: types.Callsign) -> Optional[AircraftProperties]:
        cmd_str = f"POS {callsign}"
        props = self._tmp_stack_cmd_handle_list(cmd_str, resp_expected=True)
        # TODO https://github.com/alan-turing-institute/bluesky/blob/master/bluesky/traffic/traffic.py#L541
        raise NotImplementedError(f"(Unhandled) POS returned: {props}")

    def get_all_properties(self) -> List[AircraftProperties]:
        cmd_str = f"LISTAC"
        callsigns = self._tmp_stack_cmd_handle_list(cmd_str, resp_expected=True)
        raise NotImplementedError(f"(Unhandled) LISTAC returned: {callsigns}")

    def _tmp_stack_cmd_handle_list(
        self, cmd_str: str, resp_expected: bool = False
    ) -> Optional[str]:
        resp = self._client.send_stack_cmd(cmd_str, resp_expected)
        if isinstance(resp, list):
            raise ValueError("Got a list response")

        return resp


class BlueSkySimulatorControls(AbstractSimulatorControls):
    """
    AbstractSimulatorControls implementation for BlueSky
    """

    @property
    def stream_data(self) -> SimProperties:
        raise NotImplementedError

    @property
    def properties(self) -> Union[SimProperties, str]:
        # TODO This may be difficult to get from the stack command
        raise NotImplementedError

    def __init__(self, sim_client):
        self._sim_client = sim_client

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

    def set_speed(self, speed: float) -> Optional[str]:
        raise NotImplementedError

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def get_seed(self) -> int:
        raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        raise NotImplementedError


class BlueSkyWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for BlueSky
    """

    def __init__(self, sim_client):
        self._sim_client = sim_client

    def get_all_waypoints(self) -> dict:
        raise NotImplementedError

    def define(self, name: str, position: types.LatLon, **kwargs) -> Optional[str]:
        raise NotImplementedError


class SimClient(AbstractSimClient):
    """
    AbstractSimClient implementation for BlueSky
    """

    @property
    def aircraft(self) -> BlueSkyAircraftControls:
        return self._aircraft_controls

    @property
    def simulation(self) -> BlueSkySimulatorControls:
        return self._sim_controls

    @property
    def sim_version(self) -> VersionInfo:
        return self._client.host_version

    @property
    def waypoints(self) -> BlueSkyWaypointControls:
        return self._waypoint_controls

    def __init__(self):
        self._client = BlueSkyClient()
        self._aircraft_controls = BlueSkyAircraftControls(self._client)
        self._sim_controls = BlueSkySimulatorControls(self._client)
        self._waypoint_controls = BlueSkyWaypointControls(self._client)

    def start_timers(self) -> Iterable[Timer]:
        return [self._client.start_timer()]

    def connect(self, timeout=1) -> None:
        self._client.connect(
            Settings.SIM_HOST,
            event_port=Settings.BS_EVENT_PORT,
            stream_port=Settings.BS_STREAM_PORT,
            timeout=timeout,
        )

    def stop(self, shutdown_sim: bool = False) -> bool:
        self._client.stop()
        return True
