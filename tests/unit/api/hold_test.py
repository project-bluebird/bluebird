"""
Tests for the HOLD endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    def __init__(self):
        self._pause_flag = False

    def pause(self):
        if not self._pause_flag:
            self._pause_flag = True
            return "Error: Couldn't pause sim"
        return None


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_hold_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/hold"

    # Test mode check

    Settings.SIM_MODE = SimMode.Agent

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Can't pause while in agent mode"

    Settings.SIM_MODE = SimMode.Sandbox

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't pause sim"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.OK
