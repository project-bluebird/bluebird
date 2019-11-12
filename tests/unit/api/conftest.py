"""
Configuration for the api tests
"""

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


class MockSimProxy:
    def __init__(self):
        self.last_cfl = None

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


class MockBlueBird:
    def __init__(self):
        self.sim_proxy = MockSimProxy()


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
