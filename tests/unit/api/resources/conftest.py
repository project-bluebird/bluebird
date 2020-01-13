"""
Configuration for the api tests
"""

import mock
import pytest

import bluebird.api.resources.utils.utils as utils
import bluebird.api as bluebird_api


@pytest.fixture
def test_flask_client():
    """Provides a Flask test client for the API tests"""
    with bluebird_api.FLASK_APP.test_client() as test_client:
        yield test_client


@pytest.fixture
def app_mock(test_flask_client):
    app_mock = mock.Mock()
    test_flask_client.application.config[utils.FLASK_CONFIG_LABEL] = app_mock
    return app_mock
