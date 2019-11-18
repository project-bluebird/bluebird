"""
Tests for the IC endpoint
"""

import datetime
from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.settings as settings
from bluebird.utils.properties import SimMode, SimProperties, SimState

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/ic"


class MockSimulatorControls:
    @property
    def properties(self):
        if not self._props_called:
            self._props_called = True
            return "Error: Couldn't get the sim properties"
        return SimProperties(
            SimState.RUN, 1.0, 1.0, 0.0, datetime.datetime.now(), "test_scn"
        )

    def __init__(self):
        self._props_called = False
        self.last_scn = None

    def load_scenario(self, scenario_name: str, speed: float, start_paused: bool):
        assert isinstance(scenario_name, str)
        assert isinstance(speed, float)
        assert isinstance(start_paused, bool)
        if not self.last_scn:
            self.last_scn = 1
            return "Error: Couldn't load scenario"
        self.last_scn = {
            "scenario_name": scenario_name,
            "speed": speed,
            "start_paused": start_paused,
        }


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


# pylint: disable=unused-argument


def test_ic_get(test_flask_client, _set_bb_app):
    """
    Tests the GET method
    """

    # Test error handling

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    # Test valid response

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"scn_name": "test_scn"}


def test_ic_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"filename": "", "multiplier": -1.0}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No filename specified"

    # Test multiplier check

    test_scenario = "new_scenario.json"
    data["filename"] = test_scenario
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f"Invalid speed {data['multiplier']}"

    data["multiplier"] = 1.5

    # Test error handling

    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't load scenario"

    # Test load_scenario - Sandbox mode

    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK

    load_scn_args = api_utils.sim_proxy().simulation.last_scn
    expected_args = {
        "scenario_name": test_scenario,
        "speed": 1.5,
        "start_paused": False,
    }
    assert load_scn_args == expected_args

    # Test load_scenario - Agent mode

    settings.Settings.SIM_MODE = SimMode.Agent
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK

    load_scn_args = api_utils.sim_proxy().simulation.last_scn
    expected_args["start_paused"] = True
    assert load_scn_args == expected_args
