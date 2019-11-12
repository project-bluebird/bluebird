"""
Tests for the DEFWPT endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX
from tests.unit.api import TEST_LAT, TEST_LON


def test_cre_post(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    resp = test_flask_client.post(f"{API_PREFIX}/defwpt")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"wpname": "", "lat": 91, "lon": TEST_LON}
    resp = test_flask_client.post(f"{API_PREFIX}/defwpt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be provided"

    data["wpname"] = "WPT1"
    resp = test_flask_client.post(f"{API_PREFIX}/defwpt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    data["lat"] = TEST_LAT
    resp = test_flask_client.post(f"{API_PREFIX}/defwpt", json=data)
    assert resp.status_code == HTTPStatus.CREATED

    data["type"] = "XXX"
    resp = test_flask_client.post(f"{API_PREFIX}/defwpt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["type"] = "FIX"
    resp = test_flask_client.post(f"{API_PREFIX}/defwpt", json=data)
    assert resp.status_code == HTTPStatus.CREATED
