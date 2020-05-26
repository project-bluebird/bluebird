"""
Tests for the STEP endpoint
"""
from http import HTTPStatus
from unittest import mock

from bluebird.settings import Settings
from bluebird.utils.properties import SimMode
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "step"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_step_post(test_flask_client):
    """Tests the POST method"""

    # Test agent mode check

    Settings.SIM_MODE = SimMode.Sandbox

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Must be in agent mode to use step"

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from step

        sim_proxy_mock.simulation.step.return_value = "Error"

        Settings.SIM_MODE = SimMode.Agent

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        # Test valid response

        sim_proxy_mock.simulation.step.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
