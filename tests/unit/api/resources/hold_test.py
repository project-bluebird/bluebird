"""
Tests for the HOLD endpoint
"""
from http import HTTPStatus

import mock

from bluebird.settings import Settings
from bluebird.utils.properties import SimMode
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "hold"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_hold_post(test_flask_client):
    """Tests the POST method"""

    # Test mode check

    Settings.SIM_MODE = SimMode.Agent

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Can't pause while in agent mode"

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation pause

        sim_proxy_mock.simulation.pause.return_value = "Couldn't pause sim"

        Settings.SIM_MODE = SimMode.Sandbox

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't pause sim"

        # Test valid response

        sim_proxy_mock.simulation.pause.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
