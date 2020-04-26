"""
Tests for the METRIC and METRICPROVIDERS endpoints
"""
from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils
from tests.unit.api.resources import endpoint_path


_ENDPOINT = "metric"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)

_ENDPOINT_MP = "metricproviders"
_ENDPOINT_MP_PATH = endpoint_path(_ENDPOINT_MP)


def test_metric_get(test_flask_client):
    """Tests the GET method"""

    with mock.patch("bluebird.api.resources.metrics.utils", wraps=utils) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test no providers available

        sim_proxy_mock.metrics_providers = None

        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?provider=TestProvider&name=,")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "No metrics available"

        # Test arg parsing

        sim_proxy_mock.metrics_providers = True

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

        arg_str = f"name=&"
        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{arg_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Metric name must be specified"

        # Test invalid provider

        sim_proxy_mock.metrics_providers = mock.Mock()
        sim_proxy_mock.metrics_providers.get.return_value = None

        arg_str = f"provider=TestProvider&name=TEST&"

        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{arg_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == 'Provider "TestProvider" not found'

        # Test invalid metric name

        class TestProvider:
            def version(self):
                return "1.2.3"

            def __str__(self):
                return "TestProvider"

        sim_proxy_mock.metrics_providers.get.return_value = TestProvider()
        sim_proxy_mock.call_metric_function.side_effect = AttributeError()

        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{arg_str}")
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert (
            resp.data.decode() == "Provider TestProvider (version 1.2.3) has no metric "
            "named 'TEST'"
        )

        # Test general exception from call_metric_function

        sim_proxy_mock.call_metric_function.side_effect = Exception("Error")

        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{arg_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("Metric function returned an error: Error")

        # Test valid response

        sim_proxy_mock.call_metric_function.side_effect = None
        sim_proxy_mock.call_metric_function.return_value = 123

        resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{arg_str}")
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {"TEST": 123}


def test_metricproviders_get(test_flask_client):
    """Tests the GET method"""

    with mock.patch("bluebird.api.resources.metrics.utils") as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test valid response

        class TestProvider:
            def version(self):
                return "1.2.3"

            def __str__(self):
                return "TestProvider"

        provider = TestProvider()

        sim_proxy_mock.metrics_providers = [provider]

        resp = test_flask_client.get(_ENDPOINT_MP_PATH)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {str(provider): provider.version()}
