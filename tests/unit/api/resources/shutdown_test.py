"""
Tests for the SHUTDOWN endpoint
"""
from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "shutdown"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_shutdown_post(test_flask_client):
    """Tests the POST method"""

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error when no shutdown function available

        sim_proxy_mock.shutdown.return_value = False

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert (
            resp.data.decode()
            == "No shutdown function available. (Sim shutdown ok = False)"
        )

        # Test exception from shutdown method

        sim_proxy_mock.shutdown.return_value = True

        def throwy_mc_throwface():
            raise Exception("Error")

        resp = test_flask_client.post(
            _ENDPOINT_PATH,
            environ_base={"werkzeug.server.shutdown": throwy_mc_throwface},
        )
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert (
            resp.data.decode() == "Could not shutdown: Error. (Sim shutdown ok = True)"
        )

        # Test valid response

        resp = test_flask_client.post(
            _ENDPOINT_PATH, environ_base={"werkzeug.server.shutdown": lambda: None},
        )
        assert resp.status_code == HTTPStatus.OK
        assert resp.data.decode() == "BlueBird shutting down! (Sim shutdown ok = True)"
