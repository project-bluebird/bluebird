"""
Configuration for the api tests
"""

import pytest

import bluebird.api as bluebird_api


@pytest.fixture
def test_flask_client():
    """Provides a Flask test client for the API tests"""
    bluebird_api.FLASK_APP.config["TESTING"] = True
    yield bluebird_api.FLASK_APP.test_client()
