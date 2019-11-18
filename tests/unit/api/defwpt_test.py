"""
Tests for the DEFWPT endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird, TEST_LAT, TEST_LON


class MockWaypointControls:
    """Mock WaypointControls for the DEFWPT tests"""

    def __init__(self):
        self.last_wpt = None

    def define(self, name: str, position: types.LatLon, **kwargs):
        assert isinstance(name, str)
        assert isinstance(position, types.LatLon)
        assert "type" in kwargs
        self.last_wpt = None
        if kwargs["type"] and kwargs["type"] != "FIX":
            return "Invalid waypoint type"
        self.last_wpt = {"name": name, "position": position, **kwargs}


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, None, MockWaypointControls())
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_defwpt_post(test_flask_client, _set_bb_app):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/defwpt"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"wpname": "", "lat": 91, "lon": TEST_LON}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be provided"

    # Test LatLon created

    data["wpname"] = "WPT1"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    # Test define_waypoint

    data["lat"] = TEST_LAT
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED

    data["type"] = "AAA"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["type"] = "FIX"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED
