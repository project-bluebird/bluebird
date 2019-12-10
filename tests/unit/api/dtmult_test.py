"""
Tests for the DTMULT endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    def set_speed(self, speed: float):
        assert isinstance(speed, float)
        return None if speed < 50 else "Requested speed too large"


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_dtmult_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/dtmult"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test multiplier check

    data = {"multiplier": -1}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Multiplier must be greater than 0"

    # Test set_sim_speed

    data = {"multiplier": 100}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Requested speed too large"

    data = {"multiplier": 10}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
