"""
Tests for the HDG endpoint
"""
from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as api_utils
from bluebird.api.resources.utils.responses import bad_request_resp
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "hdg"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_hdg_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {api_utils.CALLSIGN_LABEL: "FAKE"}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["hdg"] = "aaa"
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test aircraft exists check

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        data["hdg"] = 123

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test error from set_heading

        utils_patch.check_exists.return_value = None
        sim_proxy_mock.aircraft.set_heading.return_value = "Couldn't set heading"

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't set heading"

        # Test valid response

        sim_proxy_mock.aircraft.set_heading.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
