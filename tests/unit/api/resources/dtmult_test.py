"""
Tests for the DTMULT endpoint
"""
from http import HTTPStatus
from unittest import mock

import bluebird.api.resources.utils.utils as utils
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "dtmult"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_dtmult_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test multiplier check

    data = {"multiplier": -1}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Multiplier must be greater than 0"

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from set_sim_speed

        sim_proxy_mock.simulation.set_speed.return_value = "Couldn't set speed"

        data["multiplier"] = 10
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't set speed"

        # Test valid response

        sim_proxy_mock.simulation.set_speed.return_value = None
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
