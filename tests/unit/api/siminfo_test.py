"""
Tests for the SIMINFO endpoint
"""

import datetime
from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.utils.properties import SimProperties, SimState
from bluebird.utils.types import Callsign

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockAircraftControls:
    @property
    def callsigns(self):
        if not self._call_count:
            self._call_count = 1
            return "Error"
        self._call_count += 1
        return [] if self._call_count < 3 else [Callsign("TEST1"), Callsign("TEST2")]

    def __init__(self):
        self._call_count = None


class MockSimulatorControls:
    @property
    def properties(self):
        if not self._props_called:
            self._props_called = True
            return "Error"
        return SimProperties(
            SimState.RUN, 1.0, 1.0, 0.0, datetime.datetime.now(), "test_scn"
        )

    def __init__(self):
        self._props_called = False


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_siminfo_get(test_flask_client, _set_bb_app):  # pylint: disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/siminfo"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Couldn't get the sim properties: Error"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Couldn't get the callsigns: Error"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK

    expected = {
        "callsigns": [],
        "mode": "Sandbox",
        "scn_name": "test_scn",
        "sim_speed": 1.0,
        "sim_state": "RUN",
        "sim_time": 0.0,
        "sim_type": "BlueSky",
        "step_size": 1.0,
    }
    assert resp.json == expected

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK

    expected["callsigns"] = ["TEST1", "TEST2"]
    assert resp.json == expected
