"""
Tests for the SHUTDOWN endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    def __init__(self):
        self.last_seed = None

    def set_seed(self, seed: int):
        assert isinstance(seed, int)
        if not self.last_seed:
            self.last_seed = 1
            return "Error: Couldn't set the seed"
        self.last_seed = seed


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_seed_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/seed"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "value" in resp.json["message"]

    data = {"value": ""}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "value" in resp.json["message"]

    # Test seed range checking

    data = {"value": -1}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp.data.decode()
        == "Invalid seed specified. Must be a positive integer less than 2^32"
    )

    data = {"value": 2 ** 32}  # Max value allowed by np.random.seed()
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp.data.decode()
        == "Invalid seed specified. Must be a positive integer less than 2^32"
    )

    # Test set_seed

    data = {"value": 123}

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't set the seed"

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK

    assert api_utils.sim_proxy().simulation.last_seed == 123
