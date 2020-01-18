"""
Tests for the SPD endpoint
"""
from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "spd"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_spd_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data = {utils.CALLSIGN_LABEL: "AAA"}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "spd" in resp.json["message"]

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        sim_proxy_patch = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_patch

        # Test callsign exists check

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        data["spd"] = 123
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test error from set_ground_speed

        utils_patch.check_exists.return_value = None
        sim_proxy_patch.aircraft.set_ground_speed.return_value = "Error"

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        # Test valid response

        sim_proxy_patch.aircraft.set_ground_speed.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
