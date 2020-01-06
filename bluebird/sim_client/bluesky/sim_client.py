"""
BlueSky simulation client class
"""

# TODO: Need to re-add the tests for string parsing/units from the old API tests

import os
from typing import List

from semver import VersionInfo

from .bluesky_aircraft_controls import BlueSkyAircraftControls
from .bluesky_simulator_controls import BlueSkySimulatorControls
from .bluesky_waypoint_controls import BlueSkyWaypointControls
from bluebird.settings import Settings
from bluebird.sim_client.bluesky.bluesky_client import BlueSkyClient
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.utils.timer import Timer


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


class SimClient(AbstractSimClient):
    """AbstractSimClient implementation for BlueSky"""

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

    def __init__(self, **kwargs):
        self._client = BlueSkyClient()
        self._aircraft_controls = BlueSkyAircraftControls(self._client)
        self._sim_controls = BlueSkySimulatorControls(self._client)
        self._waypoint_controls = BlueSkyWaypointControls(self._client)

    def start_timers(self) -> List[Timer]:
        return self._client.start_timers()

    def connect(self, timeout=1) -> None:
        self._client.connect(
            Settings.SIM_HOST,
            event_port=Settings.BS_EVENT_PORT,
            stream_port=Settings.BS_STREAM_PORT,
            timeout=timeout,
        )

    def shutdown(self, shutdown_sim: bool = False) -> bool:
        self._client.stop()
        return True
