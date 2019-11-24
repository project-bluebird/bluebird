"""
Tests for the DIRECT endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockAircraftControls:
    """Mock WaypointControls for the DIRECT tests"""

    def __init__(self):
        self._waypoint_added = False
        self._direct_called = False

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        return (
            "Error: Invalid callsign"
            if str(callsign) == "ERR"
            # "TEST*" aircraft exist, all others do not
            else str(callsign).upper().startswith("TEST")
        )

    def direct_to_waypoint(self, callsign: types.Callsign, waypoint: types.Waypoint):
        assert isinstance(callsign, types.Callsign)
        assert isinstance(waypoint, types.Waypoint)
        if not self._direct_called:
            self._direct_called = True
            return "Error: Couldn't issue instruction"
        return None


class MockWaypointControls:
    """Mock WaypointControls for the DEFWPT tests"""

    def __init__(self):
        self.last_wpt = None

    def find(self, waypoint_name: str):  # -> Optional[types.Waypoint]:
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


def test_direct_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/direct"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {api_utils.CALLSIGN_LABEL: "T"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    data[api_utils.CALLSIGN_LABEL] = "FAKE"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test waypoint check

    data["waypoint"] = ""
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be specified"

    data["waypoint"] = "FAKE"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Could not find waypoint FAKE"

    # Test callsign check

    data["waypoint"] = "FIX1"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    # Test direct_to_waypoint

    data[api_utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Error: Couldn't issue instruction"

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
