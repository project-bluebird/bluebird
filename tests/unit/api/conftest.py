"""
Configuration for the api tests
"""

import pytest

from bluebird.utils.properties import AircraftProperties
import bluebird.api as bluebird_api
import bluebird.api.resources.utils.utils as api_utils
from bluebird.utils.properties import SimProperties, SimState
from bluebird.utils.types import (
    Callsign,
    Altitude,
    GroundSpeed,
    Heading,
    LatLon,
    VerticalSpeed,
)

import bluebird.sim_proxy.sim_proxy as sim_proxy


@pytest.fixture(autouse=True)
def patch_streaming(monkeypatch):
    """
    Set streaming mode on so that all the sim_proxy functions call through to sim_client
    instead of trying to use the internal state
    """
    monkeypatch.setattr(sim_proxy, "_is_streaming", lambda x: True)


class MockAircraftControls:
    """
    Simple test mock of AbstractAircraftControls
    """

    def __init__(self):
        self.created_aricraft = None
        self._set_hdg_called = False

    def create(self, *args):
        self.created_aricraft = list(args)

    def direct_to_waypoint(self, callsign: Callsign, waypoint: str):
        assert isinstance(callsign, Callsign)
        if not waypoint.upper() == "FIX":
            return "Invalid waypoint"
        return None

    def set_heading(self, callsign: Callsign, heading: Heading):
        if not self._set_hdg_called:
            self._set_hdg_called = True
            raise NotImplementedError
        assert isinstance(heading, Heading)
        if not str(callsign) == "TEST":
            return "Invalid callsign"
        return None


class MockSimClient:
    """
    Simple test mock of a SimClient
    """

    @property
    def aircraft(self):
        return self._aircraft_controls

    def __init__(self):
        self._aircraft_controls = MockAircraftControls()


class MockSimProxy:
    """
    Simple test mock of the SimProxy class
    """

    @property
    def sim_properties(self) -> SimProperties:
        if not self._props_called:
            self._props_called = True
            raise AttributeError
        return SimProperties(SimState.RUN, 1.0, 1.0, 0.0, "test_scn")

    def __init__(self):
        self.last_cfl = self.last_wpt = self.last_direct = self.last_scn = None
        self._props_called = self._reset_flag = self._pause_called = False
        self._get_route_called = False

    def set_cleared_fl(self, callsign: Callsign, flight_level: Altitude, **kwargs):
        self.last_cfl = {"callsign": callsign, "flight_level": flight_level, **kwargs}

    def get_aircraft_props(self, callsign: Callsign):
        if not self.contains(callsign):
            return (None, 31)
        return (
            AircraftProperties(
                "A380",
                Altitude(18_500),
                callsign,
                Altitude(22_000),
                GroundSpeed(53),
                Heading(74),
                LatLon(51.529761, -0.127531),
                Altitude(25_300),
                VerticalSpeed(73),
            ),
            42,
        )

    def contains(self, callsign: Callsign):
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def define_waypoint(self, name: str, position: LatLon, **kwargs):
        self.last_wpt = None
        if kwargs["type"] and kwargs["type"] != "FIX":
            return "Invalid waypoint type"
        self.last_wpt = {"name": name, "position": position, **kwargs}

    def direct_to_waypoint(self, callsign: Callsign, waypoint: str):
        self.last_direct = {"callsign": callsign, "waypoint": waypoint}

    def set_sim_speed(self, speed: float):
        return None if speed < 50 else "Requested speed too large"

    def reset_sim(self):
        if self._reset_flag:
            return None
        self._reset_flag = True
        return "Error!"

    def pause_sim(self):
        if not self._pause_called:
            self._pause_called = True
            return "Couldn't pause sim"
        return None

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ):
        self.last_scn = {
            "scenario_name": scenario_name,
            "speed": speed,
            "start_paused": start_paused,
        }

    def get_aircraft_route(self, callsign: Callsign):
        assert callsign
        if not self._get_route_called:
            self._get_route_called = True
            return "Could not get aircraft route"
        return ["A", "B"]  # TODO What should the route look like?


class MockBlueBird:
    def __init__(self):
        self.sim_proxy = MockSimProxy()
        self.sim_client = MockSimClient()


@pytest.fixture
def patch_bb_app(monkeypatch):
    """
    Patches the _bb_app function in the api utils module
    """
    mock_bluebird = MockBlueBird()

    def yield_mock():
        return mock_bluebird

    monkeypatch.setattr(api_utils, "_bb_app", yield_mock)


@pytest.fixture
def test_flask_client():
    """
    Provides a Flask test client for BlueBird
    """

    bluebird_api.FLASK_APP.config["TESTING"] = True
    yield bluebird_api.FLASK_APP.test_client()
