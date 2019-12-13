"""
Tests for the METRIC and METRICPROVIDERS endpoints
"""

from http import HTTPStatus

import mock
import pytest

from bluebird.metrics import MetricsProviders
from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.sim_proxy.sim_proxy import SimProxy

from bluebird.utils.debug import ASSERT_NOT_REACHED

from tests.unit import API_PREFIX


_UTILS_SIM_PROXY = "bluebird.api.resources.utils.utils.sim_proxy"


class TestProvider(AbstractMetricsProvider):
    """Test metric provider"""

    def __call__(self, metric: str, *args, **kwargs):
        ASSERT_NOT_REACHED("call_metric_function")
        assert isinstance(metric, str)
        if not metric == "TEST":
            raise AttributeError
        assert len(args) == 1, "Invalid args"
        return int(args[0])

    def __str__(self):
        return "TestProvider"

    def version(self):
        return "0.0.0"


@pytest.fixture
def sim_proxy_fixture():
    def apply_fixture(with_test_provider: bool):
        providers = [TestProvider()] if with_test_provider else []
        # Create the SimProxy Mock
        sim_proxy_mock = mock.create_autospec(spec=SimProxy, wraps=SimProxy)
        sim_proxy_mock.metrics_providers = MetricsProviders(providers)
        # Patch the API utils function
        sim_proxy_function_patch = mock.patch(_UTILS_SIM_PROXY)
        sim_proxy_function = sim_proxy_function_patch.start()
        # Attach the mock to the API utils function
        sim_proxy_function.return_value = sim_proxy_mock
        return sim_proxy_mock

    return apply_fixture


def test_metric_get_no_providers(test_flask_client, sim_proxy_fixture):
    """Tests the GET method when there are no metrics providers available"""

    sim_proxy_fixture(with_test_provider=False)

    resp = test_flask_client.get(f"{API_PREFIX}/metric?provider=TestProvider&name=,")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "No metrics available"


def test_metric_get(test_flask_client, sim_proxy_fixture):
    """Tests the GET method"""

    sim_proxy_mock: SimProxy = sim_proxy_fixture(with_test_provider=True)

    endpoint = f"{API_PREFIX}/metric"

    # Test arg parsing

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    arg_str = f"name=&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Metric name must be specified"

    # Test invalid metric name

    sim_proxy_mock.call_metric_function.side_effect = AttributeError("foo")

    arg_str = f"provider=TestProvider&name=AAA&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert (
        resp.data.decode() == "Provider TestProvider (version 0.0.0) has no metric "
        "named 'AAA'"
    )

    # Test metric args parsing

    arg_str = f"provider=TestProvider&name=TEST&"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith(
        "Metric function returned an error"  #: Invalid args"
    )

    # Test valid args
    arg_str = f"provider=TestProvider&name=TEST&args=123"
    resp = test_flask_client.get(f"{endpoint}?{arg_str}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"TEST": 123}


def test_metricproviders_get(test_flask_client):
    """Tests the GET method"""

    endpoint = f"{API_PREFIX}/metricproviders"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK
    # assert resp.json == {str(Provider()): Provider().version()}
