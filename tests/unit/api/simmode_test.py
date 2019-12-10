"""
Tests for the SIMMODE endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird, MockSimProxy


def _mock_set_mode(self, mode: SimMode):
    assert isinstance(mode, SimMode)

    if not hasattr(_mock_set_mode, "_called_flag"):
        _mock_set_mode._called_flag = True
        return "Error: Could not set mode"
    return None


@pytest.fixture
def _set_bb_app(monkeypatch):
    setattr(MockSimProxy, "set_mode", _mock_set_mode)
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_simmode_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    pytest.xfail("Endpoint disabled")

    endpoint = f"{API_PREFIX}/simmode"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "mode" in resp.json["message"]

    Settings.SIM_MODE = SimMode.Agent
    data = {"mode": "FAKE"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert (
        resp.data.decode()
        == 'Mode "FAKE" not supported. Must be one of: Sandbox, Agent'
    )

    data["mode"] = "agent"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
    assert resp.data.decode() == "Already in Agent mode!"

    data["mode"] = "sandbox"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Could not set mode"

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
