"""
MachColl simulation client class

NOTE: The assumed MachColl state transitions are -
Init        -> Running, Stepping
Running     -> Paused, Stopped
Stopped     -> Running, Stepping
Paused      -> Running, Stepping, Stopped
Stepping    -> Paused, Stopped

TODO: Check if Stopped is indeed the "terminal" state (the implementation below assumes
this is the case). If so, why can we increment from it?
"""

import logging
import os
import sys
from typing import Iterable, Optional, List, Union, Dict

from semver import VersionInfo

from bluebird.settings import is_agent_mode, Settings
from bluebird.sim_client.abstract_sim_client import (
    AbstractAircraftControls,
    AbstractSimulatorControls,
    AbstractWaypointControls,
    AbstractSimClient,
)
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties, SimProperties, SimState
from bluebird.utils.timer import Timer

_LOGGER = logging.getLogger(__name__)

# Attempt to import the MCClientMetrics class from the machine_college module.
# TODO This should work with both the package installation from pip, or from the package
# root as specified in MC_PATH. Not sure which should be the default.
try:
    from nats.machine_college.bluebird_if.mc_client_metrics import MCClientMetrics
except ModuleNotFoundError:
    _LOGGER.warning(
        "Could not find the nats package in sys.path. Attempting to look in "
        "MC_PATH instead"
    )
    _MC_PATH = os.getenv("MC_PATH", None)
    assert _MC_PATH, "Expected MC_PATH to be set. Check the .env file"
    _MC_PATH = os.path.abspath(_MC_PATH)
    assert os.path.isdir(_MC_PATH) and "nats" in os.listdir(
        _MC_PATH
    ), "Expected MC_PATH to point to the root nats directory"
    sys.path.append(_MC_PATH)
    from nats.machine_college.bluebird_if.mc_client_metrics import MCClientMetrics


_MC_MIN_VERSION = os.getenv("MC_MIN_VERSION")
if not _MC_MIN_VERSION:
    raise ValueError("The MC_MIN_VERSION environment variable must be set")

MIN_SIM_VERSION = VersionInfo.parse(_MC_MIN_VERSION)


def _raise_for_no_data(data):
    assert data, "No data received from the simulator"


class MachCollAircraftControls(AbstractAircraftControls):
    """
    AbstractAircraftControls implementation for MachColl
    """

    @property
    def stream_data(self) -> List[AircraftProperties]:
        raise NotImplementedError

    @property
    def routes(self) -> Dict[types.Callsign, List]:
        resp = self._mc_client().get_active_callsigns()
        _raise_for_no_data(resp)
        routes = {}
        for callsign_str in resp:
            callsign = types.Callsign(callsign_str)
            # TODO: Check that a None response *only* implies a connection error
            route = self._mc_client().get_flight_plan_for_callsign(str(callsign))
            # TODO: Check the type of route
            routes[callsign] = route
        return routes

    def __init__(self, sim_client):
        self._sim_client = sim_client
        self._lookup = None

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        err = self._mc_client().set_cfl_for_callsign(
            str(callsign), flight_level.flight_levels
        )
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

    def get_properties(
        self, callsign: types.Callsign
    ) -> Union[AircraftProperties, str]:
        resp = self._mc_client().get_active_flight_by_callsign(str(callsign))
        _raise_for_no_data(resp)
        return self._parse_aircraft_properties(resp)

    def get_all_properties(self) -> Dict[types.Callsign, AircraftProperties]:
        resp = self._mc_client().get_active_callsigns()
        _raise_for_no_data(resp)
        all_props = {}
        for callsign_str in resp:
            callsign = types.Callsign(callsign_str)
            props = self.get_properties(callsign)
            all_props[callsign] = props
        return all_props

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    @staticmethod
    def _parse_aircraft_properties(ac_props: dict) -> Union[AircraftProperties, str]:
        try:
            alt = types.Altitude("FL" + str(ac_props["pos"]["afl"]))
            # TODO Check this is appropriate
            rfl_val = ac_props["flight-plan"]["rfl"]
            rfl = types.Altitude("FL" + str(rfl_val)) if rfl_val else alt
            # TODO Not currently available: gs, hdg, pos, vs
            return AircraftProperties(
                ac_props["flight-data"]["type"],
                alt,
                types.Callsign(ac_props["flight-data"]["callsign"]),
                types.Altitude("FL" + str(ac_props["instruction"]["cfl"])),
                types.GroundSpeed(ac_props["pos"]["speed"]),
                types.Heading(0),
                types.LatLon(ac_props["pos"]["lat"], ac_props["pos"]["long"]),
                rfl,
                types.VerticalSpeed(0),
            )
        except Exception as exc:  # pylint: disable=broad-except
            return f"Error parsing AircraftProperties: {exc}"


class MachCollSimulatorControls(AbstractSimulatorControls):
    """
    AbstractSimulatorControls implementation for MachColl
    """

    @property
    def stream_data(self) -> SimProperties:
        raise NotImplementedError

    @property
    def properties(self) -> Union[SimProperties, str]:
        responses = []
        for req in [
            self._mc_client().get_state,
            self._mc_client().get_speed,
            self._mc_client().get_step,
            self._mc_client().get_time,
        ]:
            responses.append(req())
            if not responses[-1]:
                return f"Could not get property from sim ({req.__name__})"

        try:
            responses[0] = self.parse_sim_state(responses[0])
        except ValueError as exc:
            return str(exc)

        # Different type returned on failure, have to handle separately
        responses.append(self._mc_client().get_scenario_filename())
        if not isinstance(responses[-1], str):
            return f"Could not get the current scenario name: {responses[-1]}"

        try:
            assert len(responses) == len(
                SimProperties.__annotations__  # pylint: disable=no-member
            )
            return SimProperties(*responses)  # Splat!
        except Exception as exc:  # pylint: disable=broad-except
            return str(exc)

    def __init__(self, sim_client):
        self._sim_client = sim_client

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        _LOGGER.debug(f"Loading {scenario_name}")
        _LOGGER.warning(f"Unhandled arguments: speed, start_paused")
        resp = self._mc_client().set_scenario_filename(scenario_name)
        # TODO Check this is as expected. MCClient docstring suggests that an error
        # response will be returned on failure, however currently None is returned on
        # failure and the scenario name is passed back on success
        if not resp:
            return "Error: No confirmation received from MachColl"
        return None

    # TODO Assert state is as expected after all of these methods (should be in the
    # response)
    def start(self) -> Optional[str]:
        # NOTE: If agent mode, no need to explicitly start since we can step from init
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == SimState.RUN:
            return
        resp = self._mc_client().sim_start()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def reset(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == SimState.INIT:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def pause(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state in [SimState.INIT, SimState.HOLD, SimState.END]:
            return None
        resp = self._mc_client().sim_pause()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def resume(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == SimState.RUN:
            return None
        if state == SimState.END:
            return 'Can\'t resume sim from "END" state'
        resp = self._mc_client().sim_resume()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def stop(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == SimState.END:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    @staticmethod
    def parse_sim_state(val: str) -> SimState:
        # TODO There is also a possible "stepping" mode (?)
        if val.upper() == "INIT":
            return SimState.INIT
        if val.upper() == "RUNNING":
            return SimState.RUN
        if val.upper() == "STOPPED":
            return SimState.END
        if val.upper() == "PAUSED":
            return SimState.HOLD
        raise ValueError(f'Unknown state: "{val}"')

    def step(self) -> Optional[str]:
        # TODO: Work-in the other metrics. Do we want to get every metric at every step?
        self._mc_client().queue_metrics_query("metrics.score")
        resp = self._mc_client().set_increment()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def get_speed(self) -> float:
        resp = (
            self._mc_client().get_step()
            if is_agent_mode()
            else self._mc_client().get_speed()
        )
        _raise_for_no_data(resp)
        _LOGGER.warning(f"Unhandled data: {resp}")
        return -1

    def set_speed(self, speed: float) -> Optional[str]:
        resp = (
            self._mc_client().set_step(speed)
            if is_agent_mode()
            else self._mc_client().set_speed(speed)
        )
        _raise_for_no_data(resp)
        _LOGGER.warning(f"Unhandled data: {resp}")
        return None if (resp == speed) else f"Unknown response: {resp}"

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

    def get_time(self) -> float:
        resp = self._mc_client().get_time()
        _raise_for_no_data(resp)
        return resp

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    def _get_state(self) -> Union[SimState, str]:
        state = self._mc_client().get_state()
        if not state:
            return f"Could not get the sim state"
        try:
            return self.parse_sim_state(state)
        except ValueError as exc:
            return str(exc)

    @staticmethod
    def _is_success(data) -> bool:
        try:
            return data["code"]["Short Description"] == "Success"
        except:
            pass
        return False


class MachCollWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for MachColl
    """

    def __init__(self, sim_client):
        self._sim_client = sim_client

    def get_all_waypoints(self) -> dict:
        fixes = self._mc_client().get_all_fixes()
        if not isinstance(fixes, dict):
            raise NotImplementedError(f"get_all_fixes returned: {fixes}")
        # TODO Need to create a mapping
        _LOGGER.warning(f"Unhandled data: {fixes}")
        return {}

    def define(self, name: str, position: types.LatLon, **kwargs) -> Optional[str]:
        raise NotImplementedError

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client


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
        return self._client_version

    @property
    def waypoints(self) -> AbstractWaypointControls:
        return self._waypoint_controls

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        self.mc_client = None
        self._client_version: VersionInfo = None
        self._sim_controls = MachCollSimulatorControls(self)
        self._aircraft_controls = MachCollAircraftControls(self)
        self._waypoint_controls = MachCollWaypointControls(self)

    def connect(self, timeout: int = 1) -> None:
        self.mc_client = MCClientMetrics(host=Settings.SIM_HOST, port=Settings.MC_PORT)

        # Perform a request to initialise the connection
        if not self.mc_client.get_state():
            raise TimeoutError("Could not connect to the MachColl server")

        version_dict = self.mc_client.compare_api_version()
        self._client_version = VersionInfo.parse(version_dict["This client version"])
        _LOGGER.debug(f"MCClientMetrics connected. Version: {self._client_version}")

    def start_timers(self) -> Iterable[Timer]:
        return []

    def stop(self, shutdown_sim: bool = False) -> bool:

        stop_str = self.simulation.stop()
        if stop_str:
            _LOGGER.error(f"Error when stopping simulation: {stop_str}")

        self.mc_client.close_mq()

        # NOTE: Using the presence of _client_version to infer that we have a connection
        if not self._client_version or not shutdown_sim:
            return True

        raise NotImplementedError("No sim shutdown method implemented")
