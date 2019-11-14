"""
Tests for the DEFWPT endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX
from tests.unit.api import TEST_LAT, TEST_LON


def test_defwpt_post(test_flask_client, patch_bb_app):  # pylint:disable=unused-argument
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

    data["type"] = "XXX"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["type"] = "FIX"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED
