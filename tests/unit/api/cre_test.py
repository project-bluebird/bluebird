"""
Tests for the CRE endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX
from tests.unit.api import TEST_LAT, TEST_LON, MockBlueBird


class MockAircraftControls:
    """Mock AircraftControls for the CRE tests"""

    def __init__(self):
        self.created_aircraft = None

    def create(self, *args):
        """Mock of the AircraftControls.create function"""
        assert len(args)
        self.created_aircraft = list(args)

    def exists(self, callsign: types.Callsign):
        """Mock of the SimProxy.contains function"""
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


# pylint:disable=unused-argument, redefined-outer-name


def test_cre_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/cre"

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    callsign = "T"
    data = {api_utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    callsign = "AAA"
    data = {api_utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "type" in resp.json["message"]

    data["type"] = ""
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "lat" in resp.json["message"]

    data["lat"] = 91
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "lon" in resp.json["message"]

    data["lon"] = 181
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "hdg" in resp.json["message"]

    data["hdg"] = "aaa"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["hdg"] == "Heading must be an int"

    data["hdg"] = 123
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = -1
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["alt"] == "Altitude must be positive"

    data["alt"] = "FL100"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "gspd" in resp.json["message"]

    data["gspd"] = "..."
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["gspd"] == "Ground speed must be an int"

    # Test aircraft exists

    data = {
        api_utils.CALLSIGN_LABEL: "TEST1",
        "type": "A380",
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "hdg": 123,
        "alt": 18_500,
        "gspd": 50,
    }
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft TEST1 already exists"

    # Test LatLon parse

    data[api_utils.CALLSIGN_LABEL] = "AAA"
    data["lat"] = -91
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    # Test valid aircraft creation

    data["lat"] = TEST_LAT
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED

    created_aircraft = api_utils.sim_proxy().aircraft.created_aircraft
    assert len(created_aircraft) == len(data) - 1
    assert created_aircraft[0] == types.Callsign(data[api_utils.CALLSIGN_LABEL])
    assert created_aircraft[1] == data["type"]
    assert created_aircraft[2] == types.LatLon(data["lat"], data["lon"])
    assert created_aircraft[3] == types.Heading(data["hdg"])
    assert created_aircraft[4] == types.Altitude(data["alt"])
    assert created_aircraft[5] == types.GroundSpeed(data["gspd"])
