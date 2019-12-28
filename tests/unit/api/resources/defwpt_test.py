"""
Tests for the DEFWPT endpoint
"""

from http import HTTPStatus

import bluebird.utils.types as types

from tests.unit import API_PREFIX


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


def test_defwpt_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/defwpt"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"wpname": "", "lat": 91, "lon": "1.23"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be provided"

    # Test LatLon created

    data["wpname"] = "WPT1"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    # Test define_waypoint

    data["lat"] = "1.23"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED

    data["type"] = "AAA"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["type"] = "FIX"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED
