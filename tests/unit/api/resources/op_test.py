"""
Tests for the OP endpoint
"""

from http import HTTPStatus

import mock

import bluebird.settings as settings
from bluebird.utils.properties import SimMode

from tests.unit.api.resources import endpoint_path, patch_utils_path


_ENDPOINT = "op"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_op_post_agent_mode(test_flask_client):
    """Tests the POST endpoint"""

    # Test error when in agent mode

    settings.Settings.SIM_MODE = SimMode.Agent

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Can't resume sim from mode Agent"

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation resume

        sim_proxy_mock.simulation.resume.return_value = "Couldn't resume sim"

        settings.Settings.SIM_MODE = SimMode.Sandbox

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't resume sim"

        # Test valid response

        sim_proxy_mock.simulation.resume.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
