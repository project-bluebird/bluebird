"""
Tests for the SPD endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockAircraftControls:
    def __init__(self):
        self.last_ground_speed = None

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        assert isinstance(callsign, types.Callsign)
        assert isinstance(ground_speed, types.GroundSpeed)
        if not self.last_ground_speed:
            self.last_ground_speed = True
            return "Error: Couldn't set ground speed"
        self.last_ground_speed = ground_speed
        return None


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_spd_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/spd"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    data = {api_utils.CALLSIGN_LABEL: "AAA"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "spd" in resp.json["message"]

    # Test callsign exists check

    data["spd"] = 123
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "AAA" does not exist'

    # Test set_ground_speed

    data[api_utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't set ground speed"

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
    assert api_utils.sim_proxy().aircraft.last_ground_speed == types.GroundSpeed(123)
