"""
Tests for the OP endpoint
"""

from http import HTTPStatus

import bluebird.settings as settings
from bluebird.utils.properties import SimMode

from tests.unit import API_PREFIX


_ENDPOINT = f"{API_PREFIX}/op"


class MockSimulatorControls:
    def __init__(self):
        self._reset_flag = False

    def resume(self):
        if not self._reset_flag:
            self._reset_flag = True
            return "Error: Couldn't resume simulation"
        return None


def test_op_post_agent_mode(test_flask_client, _set_bb_app):
    """
    Tests the POST method when in agent mode
    """

    settings.Settings.SIM_MODE = SimMode.Agent

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Can't resume sim from mode Agent"


def test_op_post_sandbox_mode(test_flask_client, _set_bb_app):
    """
    Tests the POST method when in sandbox mode
    """

    settings.Settings.SIM_MODE = SimMode.Sandbox

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't resume simulation"

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK
