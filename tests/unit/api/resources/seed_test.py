"""
Tests for the SHUTDOWN endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils

from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "seed"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_seed_post(test_flask_client):
    """Tests the POST method """

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "value" in resp.json["message"]

    data = {"value": ""}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "value" in resp.json["message"]

    # Test seed range checking

    data = {"value": -1}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp.data.decode()
        == "Invalid seed specified. Must be a positive integer less than 2^32"
    )

    data = {"value": 2 ** 32}  # Max value allowed by np.random.seed()
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp.data.decode()
        == "Invalid seed specified. Must be a positive integer less than 2^32"
    )

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.MagicMock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from set_seed

        sim_proxy_mock.simulation.set_seed.return_value = "Error"

        data = {"value": 123}

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        # Test valid response

        sim_proxy_mock.simulation.set_seed.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
