"""
Tests for the ALT endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/alt"


class MockAircraftControls:
    # pylint: disable=missing-docstring
    def __init__(self):
        self.last_cfl = None

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ):
        assert isinstance(callsign, types.Callsign)
        assert isinstance(flight_level, types.Altitude)
        assert "vspd" in kwargs
        self.last_cfl = {"callsign": callsign, "flight_level": flight_level, **kwargs}

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def get_properties(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        if not self.exists(callsign):
            return "Error: Could not get properties"
        return AircraftProperties(
            "A380",
            types.Altitude(18_500),
            callsign,
            types.Altitude(22_000),
            types.GroundSpeed(53),
            types.Heading(74),
            types.LatLon(51.529761, -0.127531),
            types.Altitude(25_300),
            types.VerticalSpeed(73),
        )


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


# pylint:disable=unused-argument, redefined-outer-name


def test_alt_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "X"
    data = {api_utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    data = {api_utils.CALLSIGN_LABEL: "TEST", "alt": -1}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = 0
    data["vspd"] = "..."
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "vspd" in resp.json["message"]

    # Test correct units

    callsign = "TEST"
    data = {api_utils.CALLSIGN_LABEL: callsign}
    alt = types.Altitude(12_300)
    for test_case in [alt.flight_levels, alt.feet]:
        data["alt"] = test_case
        resp = test_flask_client.post(_ENDPOINT, json=data)
        assert resp.status_code == HTTPStatus.OK
        cfl_args = api_utils.sim_proxy().aircraft.last_cfl
        assert cfl_args, "Expected set_cleared_fl to be called"
        assert str(cfl_args["callsign"]) == callsign
        assert cfl_args["flight_level"] == alt

    # Test optional arg passed to set_cleared_fl

    data["vspd"] = 20
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK
    cfl_args = api_utils.sim_proxy().aircraft.last_cfl
    assert cfl_args, "Expected set_cleared_fl to be called"
    assert cfl_args["vspd"] == types.VerticalSpeed(20), ""


def test_alt_get(test_flask_client, _set_bb_app):
    """
    Tests the GET method
    """

    # Test arg parsing

    resp = test_flask_client.get(f"{_ENDPOINT}?")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "T"
    resp = test_flask_client.get(f"{_ENDPOINT}?{api_utils.CALLSIGN_LABEL}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    # Test aircraft exists check

    callsign = "AAA"
    resp = test_flask_client.get(f"{_ENDPOINT}?{api_utils.CALLSIGN_LABEL}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft AAA does not exist"

    # Test response units

    callsign = "TEST"
    args = f"?{api_utils.CALLSIGN_LABEL}={callsign}"

    resp = test_flask_client.get(f"{_ENDPOINT}{args}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json[callsign]["fl_current"] == 18_500
    assert resp.json[callsign]["fl_cleared"] == 22_000
    assert resp.json[callsign]["fl_requested"] == 25_300
