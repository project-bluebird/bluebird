"""
Tests for the DEFWPT endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils

from tests.unit.api.resources import endpoint_path, patch_utils_path

_ENDPOINT = "defwpt"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_defwpt_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"wpname": "", "lat": 91, "lon": "1.23"}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be provided"

    # Test LatLon created

    data["wpname"] = "WPT1"
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        mock_sim_proxy = mock.Mock()
        utils_patch.sim_proxy.return_value = mock_sim_proxy

        # Test error from waypoint define

        mock_sim_proxy.waypoints.define.return_value = "Couldn't define waypoint"

        data["lat"] = 0

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't define waypoint"

        # Test valid response

        mock_sim_proxy.waypoints.define.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.CREATED
