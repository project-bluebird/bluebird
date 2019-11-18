"""
Tests for the RESET endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    def __init__(self):
        self._reset_flag = False

    def reset(self):
        if not self._reset_flag:
            self._reset_flag = True
            return "Error: Couldn't reset sim"
        return None


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_reset_post(test_flask_client, _set_bb_app):  # pylint: disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/reset"

    # Test mode check

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't reset sim"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.OK
