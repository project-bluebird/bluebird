"""
Tests for the EPINFO endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX


def test_epinfo_get(test_flask_client):
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/epinfo"

    # The endpoint is currently disabled since it is now mostly covered by the "eplog"
    # endpoint
    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.NOT_FOUND
