"""
Tests for the ALT endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils

from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "alt"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_alt_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "X"
    data = {utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data = {utils.CALLSIGN_LABEL: "TEST", "alt": -1}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = 0
    data["vspd"] = "..."
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "vspd" in resp.json["message"]

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        mock_sim_proxy = mock.Mock()
        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        utils_patch.sim_proxy.return_value = mock_sim_proxy

        # Test error from set_cleared_fl

        mock_sim_proxy.aircraft.set_cleared_fl.return_value = "Couldn't set CFL"

        data["vspd"] = 123

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't set CFL"

        # Test valid response

        mock_sim_proxy.aircraft.set_cleared_fl.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
