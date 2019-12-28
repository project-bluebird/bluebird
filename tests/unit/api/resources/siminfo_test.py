"""
Tests for the SIMINFO endpoint
"""

import datetime
from http import HTTPStatus

from bluebird.utils.properties import SimProperties, SimState
from bluebird.utils.types import Callsign

from tests.unit import API_PREFIX

_DATETIME = datetime.datetime.now()


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
            scenario_name="TEST",
            scenario_time=0,
            seed=0,
            speed=1.0,
            state=SimState.INIT,
            step_size=1.0,
            utc_time=_DATETIME,
        )

    def __init__(self):
        self._props_called = False


def test_siminfo_get(test_flask_client, _set_bb_app):
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
        "scenario_name": "TEST",
        "scenario_time": 0,
        "seed": 0,
        "sim_type": "BlueSky",
        "speed": 1.0,
        "state": "INIT",
        "step_size": 1.0,
        "utc_time": str(_DATETIME)[:-7],
    }
    assert resp.json == expected

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK

    expected["callsigns"] = ["TEST1", "TEST2"]
    assert resp.json == expected
