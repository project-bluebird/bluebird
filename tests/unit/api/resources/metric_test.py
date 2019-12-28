"""
Tests for the METRIC and METRICPROVIDERS endpoints
"""

from http import HTTPStatus

import mock

from bluebird.api.resources.utils.utils import parse_args
from bluebird.metrics import MetricsProviders
from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.utils.abstract_sim_client import AbstractSimClient

from tests.unit import API_PREFIX


_UTILS_SIM_PROXY = "bluebird.api.resources.utils.utils.sim_proxy"


class TestProvider(AbstractMetricsProvider):
    """Test metric provider"""

    def __call__(self, metric: str, *args, **kwargs):
        assert isinstance(metric, str)
        if not metric == "TEST":
            raise AttributeError
        assert len(args) == 1, "Wrong number of args"
        return int(args[0])

    def __str__(self):
        return "TestProvider"

    def version(self):
        return "0.0.0"


def test_metric_get_no_providers(test_flask_client):
    """Tests the GET method when there are no metrics providers available"""

    sim_proxy_mock = mock.Mock()
    sim_proxy_mock.metrics_providers = MetricsProviders([])

    with mock.patch("bluebird.api.resources.metrics.utils") as utils_patch:
        utils_patch.sim_proxy = mock.Mock(return_value=sim_proxy_mock)

        resp = test_flask_client.get(
            f"{API_PREFIX}/metric?provider=TestProvider&name=,"
        )
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "No metrics available"


def test_metric_get(test_flask_client):
    """Tests the GET method"""

    endpoint = f"{API_PREFIX}/metric"

    with mock.patch("bluebird.api.resources.metrics.utils") as utils_patch:

        # Test arg parsing

        utils_patch.parse_args = parse_args

        resp = test_flask_client.get(endpoint)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

        arg_str = f"name=&"
        resp = test_flask_client.get(f"{endpoint}?{arg_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Metric name must be specified"

        # Test invalid metric name

        mock_sim_client = mock.Mock(spec=AbstractSimClient)
        sim_proxy = SimProxy(mock_sim_client, MetricsProviders([TestProvider()]))
        utils_patch.sim_proxy = mock.Mock(return_value=sim_proxy)

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
            "Metric function returned an error: Wrong number of args"
        )

        # Test valid args

        arg_str = f"provider=TestProvider&name=TEST&args=123"
        resp = test_flask_client.get(f"{endpoint}?{arg_str}")
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {"TEST": 123}


def test_metricproviders_get(test_flask_client):
    """Tests the GET method"""

    endpoint = f"{API_PREFIX}/metricproviders"

    with mock.patch("bluebird.api.resources.metrics.utils") as utils_patch:

        mock_sim_client = mock.Mock(spec=AbstractSimClient)
        sim_proxy = SimProxy(mock_sim_client, MetricsProviders([TestProvider()]))
        utils_patch.sim_proxy = mock.Mock(return_value=sim_proxy)

        resp = test_flask_client.get(endpoint)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {str(TestProvider()): TestProvider().version()}
