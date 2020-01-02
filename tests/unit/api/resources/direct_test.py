"""
Tests for the DIRECT endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp

from tests.unit.api.resources import endpoint_path, patch_utils_path, TEST_WAYPOINT


_ENDPOINT = "direct"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_direct_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {utils.CALLSIGN_LABEL: "T"}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data[utils.CALLSIGN_LABEL] = "FAKE"
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test name check

    data["waypoint"] = ""
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be specified"

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        mock_sim_proxy = mock.Mock()
        utils_patch.sim_proxy.return_value = mock_sim_proxy

        # Test waypoint exists check

        mock_sim_proxy.waypoints.find.return_value = None

        data["waypoint"] = TEST_WAYPOINT.name
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == f"Could not find waypoint {TEST_WAYPOINT.name}"

        # Test callsign check

        mock_sim_proxy.waypoints.find.return_value = TEST_WAYPOINT

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test error from direct_to_waypoint

        utils_patch.check_exists.return_value = None
        mock_sim_proxy.aircraft.direct_to_waypoint.return_value = "Error"

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        # Test valid response

        mock_sim_proxy.aircraft.direct_to_waypoint.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
