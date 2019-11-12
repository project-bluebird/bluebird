"""
Configuration for the api tests
"""

from typing import Container
import pytest

from bluebird.utils.properties import AircraftProperties
import bluebird.api as bluebird_api
import bluebird.api.resources.utils.utils as api_utils
from bluebird.utils.types import (
    Callsign,
    Altitude,
    GroundSpeed,
    Heading,
    LatLon,
    VerticalSpeed,
)

import bluebird.sim_proxy.sim_proxy as sim_proxy

from tests.unit.api import TEST_LATLON


@pytest.fixture(autouse=True)
def patch_streaming(monkeypatch):
    monkeypatch.setattr(sim_proxy, "_is_streaming", lambda x: True)


class MockAircraftControls:
    """
    Simple test mock of AbstractAircraftControls
    """

    def create(self, *args, **kwargs):
        pass


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

    def __init__(self):
        self.last_cfl = None
        self.last_wpt = None

    def set_cleared_fl(self, callsign: Callsign, flight_level: Altitude, **kwargs):
        self.last_cfl = {"callsign": callsign, "flight_level": flight_level, **kwargs}

    def get_aircraft_props(self, callsign: Callsign):
        return (
            AircraftProperties(
                "A380",
                Altitude(0),
                callsign,
                Altitude(0),
                GroundSpeed(0),
                Heading(0),
                LatLon(0, 0),
                Altitude(0),
                VerticalSpeed(0),
            ),
            0,
        )

    def contains(self, callsign: Callsign):
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def define_waypoint(self, name: str, position: LatLon, **kwargs):
        if kwargs["type"] and kwargs["type"] != "FIX":
            return "Invalid waypoint type"
        self.last_wpt = {"name": name, "position": position, **kwargs}


class MockBlueBird:
    def __init__(self):
        self.sim_proxy = MockSimProxy()
        self.sim_client = MockSimClient()


@pytest.fixture
def patch_sim_proxy(monkeypatch):
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
