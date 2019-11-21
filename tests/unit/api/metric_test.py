"""
Tests for the METRIC and METRICPROVIDERS endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class Provider:
    """
    Mock metric provider
    """

    def __call__(self, metric: str, *args, **kwargs):
        assert isinstance(metric, str)
        if not metric == "TEST":
            raise AttributeError
        assert len(args) == 1, "Invalid args"
        return int(args[0])

    def __str__(self):
        return "TestProvider"

    def version(self):
        return "1.0.0"


def _set_bb_app(monkeypatch, set_provider):
    mock = MockBlueBird()
    if set_provider:
        mock.metrics_providers = [Provider()]
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


@pytest.fixture
def _set_bb_app_no_provider(monkeypatch):
    _set_bb_app(monkeypatch, False)


@pytest.fixture
def _set_bb_app_with_provider(monkeypatch):
    _set_bb_app(monkeypatch, True)


def test_metric_get_no_providers(test_flask_client, _set_bb_app_no_provider):
    """Tests the GET method when there are no metrics providers available"""

    resp = test_flask_client.get(f"{API_PREFIX}/metric?name=,")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "No metrics available"


def test_metric_get(test_flask_client, _set_bb_app_with_provider):
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/metric"

    # Test arg parsing

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    arg_str = f"name=&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Metric name must be specified"

    # Test invalid metric name

    arg_str = f"name=AAA&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert (
        resp.data.decode()
        == "Provider TestProvider (version 1.0.0) has no metric named 'AAA'"
    )

    # Test metric args parsing

    arg_str = f"name=TEST&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith(
        "Metric function returned an error: Invalid args"
    )

    # Test valid args
    arg_str = f"name=TEST&args=123"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"TEST": 123}


def test_metricproviders_get(test_flask_client, _set_bb_app_with_provider):
    """Tests the GET method"""

    endpoint = f"{API_PREFIX}/metricproviders"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {str(Provider()): Provider().version()}
