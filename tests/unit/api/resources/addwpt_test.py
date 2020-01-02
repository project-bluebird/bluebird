"""
Tests for the ADDWPT endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp

from tests.unit.api.resources import endpoint_path, patch_utils_path


_ENDPOINT = "addwpt"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_addwpt_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {utils.CALLSIGN_LABEL: "AAA"}

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test waypoint name check

    data["waypoint"] = ""
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "A waypoint name must be provided"

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        mock_sim_proxy = mock.Mock()
        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        utils_patch.sim_proxy.return_value = mock_sim_proxy

        # Test aircraft exists check

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        data["waypoint"] = "FAKE"
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test missing waypoint handling

        utils_patch.check_exists.return_value = None
        mock_sim_proxy.waypoints.find.return_value = None

        data[utils.CALLSIGN_LABEL] = "TEST"
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == 'Could not find waypoint "FAKE"'

        # Test error from add_waypoint_to_route

        mock_sim_proxy.waypoints.find.return_value = True
        mock_sim_proxy.aircraft.add_waypoint_to_route.return_value = (
            "Couldn't add to route"
        )

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't add to route"

        # Test valid response

        mock_sim_proxy.aircraft.add_waypoint_to_route.return_value = None
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
