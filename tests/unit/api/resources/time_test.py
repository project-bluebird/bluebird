"""
Tests for the TIME endpoint
"""

import datetime
from http import HTTPStatus

from bluebird.utils.properties import SimProperties, SimState

from tests.unit import API_PREFIX

_DATETIME = datetime.datetime.now()


class MockSimulatorControls:
    @property
    def properties(self):
        if not self._props_called:
            self._props_called = True
            return "Couldn't get the sim properties"
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
    assert resp.json == {"scenario_time": 0.0, "utc_time": str(_DATETIME)[:-7]}
