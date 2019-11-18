"""
Tests for the ADDWPT endpoint
"""

from http import HTTPStatus
from typing import Union

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockAircraftControls:
    """Mock WaypointControls for the DEFWPT tests"""

    def __init__(self):
        self._waypoint_added = False

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        return (
            "Error: Invalid callsign"
            if str(callsign) == "ERR"
            # "TEST*" aircraft exist, all others do not
            else str(callsign).upper().startswith("TEST")
        )

    def add_waypoint_to_route(
        self, callsign: types.Callsign, waypoint: types.Waypoint, **kwargs
    ):
        assert isinstance(callsign, types.Callsign)
        assert isinstance(waypoint, types.Waypoint)
        assert "spd" in kwargs
        if not self._waypoint_added:
            self._waypoint_added = True
            return "Error: Invalid waypoint"
        return None


class MockWaypointControls:
    """Mock WaypointControls for the DEFWPT tests"""

    def find(self, waypoint_name: str):
        assert isinstance(waypoint_name, str)
        return (
            types.Waypoint(waypoint_name, types.LatLon(45, 90), None)
            if waypoint_name.startswith("FIX")
            else None
        )


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), None, MockWaypointControls())
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_addwpt_post(test_flask_client, _set_bb_app):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/addwpt"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {api_utils.CALLSIGN_LABEL: "AAA"}

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test waypoint name check

    data["waypoint"] = ""
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "A waypoint name must be provided"

    # Test aircraft exists check

    data["waypoint"] = "FAKE"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft AAA does not exist"

    # Test find waypoint by name

    data[api_utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Could not find waypoint FAKE"

    data["waypoint"] = "FIX1"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Invalid waypoint"

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
