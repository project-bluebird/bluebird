"""
Configuration for the api tests
"""

import pytest

import bluebird.api as bluebird_api
import bluebird.sim_proxy.sim_proxy as sim_proxy


@pytest.fixture(autouse=True)
def patch_streaming(monkeypatch):
    """
    Set streaming mode on so that all the sim_proxy functions call through to sim_client
    instead of trying to use the internal state
    """
    monkeypatch.setattr(sim_proxy, "_is_streaming", lambda x: True)


@pytest.fixture
def test_flask_client():
    """Provides a Flask test client for the API tests"""
    bluebird_api.FLASK_APP.config["TESTING"] = True
    yield bluebird_api.FLASK_APP.test_client()
