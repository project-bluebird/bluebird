"""
Tests for the RESET endpoint
"""
from http import HTTPStatus

import mock

from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "reset"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_reset_post(test_flask_client):
    """Tests the POST method"""

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation reset

        sim_proxy_mock.simulation.reset.return_value = "Error"

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        sim_proxy_mock.simulation.reset.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
