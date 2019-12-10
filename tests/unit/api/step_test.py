"""
Tests for the STEP endpoint
"""

import datetime
from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    def __init__(self):
        self._was_stepped = False

    def step(self):
        if not self._was_stepped:
            self._was_stepped = True
            return "Error: Couldn't step"
        return None


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_step_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/step"

    # Test agent mode check

    Settings.SIM_MODE = SimMode.Sandbox
    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Must be in agent mode to use step"

    # Test step

    Settings.SIM_MODE = SimMode.Agent
    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't step"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.OK
