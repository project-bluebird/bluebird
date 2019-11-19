"""
Tests for the TIME endpoint
"""

import datetime
from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.utils.properties import SimProperties, SimState

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird

_DATETIME = datetime.datetime.now()


class MockSimulatorControls:
    @property
    def properties(self):
        if not self._props_called:
            self._props_called = True
            return "Couldn't get the sim properties"
        return SimProperties(SimState.RUN, 1.0, 1.0, 0.0, _DATETIME, "test_scn")

    def __init__(self):
        self._props_called = False


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_time_get(test_flask_client, _set_bb_app):
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/time"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't get the sim properties"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"scenario_time": 0.0, "sim_utc": str(_DATETIME)[:-7]}
