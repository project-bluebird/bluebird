"""
Tests for the SHUTDOWN endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird, MockSimProxy


def _mock_shutdown(self, shutdown_sim: bool = False) -> bool:
    assert isinstance(shutdown_sim, bool)

    if not hasattr(_mock_shutdown, "_called_flag"):
        _mock_shutdown._called_flag = True
        return False
    return True


@pytest.fixture
def _set_bb_app(monkeypatch):
    setattr(MockSimProxy, "shutdown", _mock_shutdown)
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


# TODO(RKM 2019-11-18) Find some way of patching the request.environ
# "werkzeug.server.shutdown" function
def test_shutdown_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/shutdown"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert (
        resp.data.decode()
        == "No shutdown function available. (Sim shutdown ok = False)"
    )

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert (
        resp.data.decode() == "No shutdown function available. (Sim shutdown ok = True)"
    )
