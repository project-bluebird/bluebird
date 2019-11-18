"""
Logic for metric endpoints
"""

import logging

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import (
    internal_err_resp,
    bad_request_resp,
    not_found_resp,
    ok_resp,
)
from bluebird.api.resources.utils.utils import metrics_providers, parse_args
from bluebird.metrics.abstract_metrics_provider import AbstractMetricProvider


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="args", required=True)
_PARSER.add_argument("args", type=str, location="args", required=False)
_PARSER.add_argument("provider", type=str, location="args", required=False)

_LOGGER = logging.getLogger(__name__)

# -> Union[RespTuple, AbstractMetricProvider]:
def _get_provider_by_name(provider_name: str):
    if not provider_name:
        return bad_request_resp("Provider name must be specified")

    provider = next((x for x in metrics_providers() if str(x) == provider_name), None)

    if not provider:
        return bad_request_resp(f"Provider {provider_name} not found")

    return provider


class Metric(Resource):
    """
    BlueBird Metrics endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Attempts to call the method for the given metric
        :return:
        """

        if not metrics_providers():
            return internal_err_resp("No metrics available")

        req_args = parse_args(_PARSER)
        metric_name = req_args["name"]

        if not metric_name:
            return bad_request_resp("Metric name must be specified")

        # BlueBird's built-in metrics
        provider = metrics_providers()[0]

        if req_args["provider"]:
            provider = _get_provider_by_name(req_args["provider"])
            if not isinstance(provider, AbstractMetricProvider):
                return provider

        args = req_args["args"].split(",") if req_args["args"] else []

        try:
            result = provider(metric_name, *args)
        # Catch cases where a wrong metric name is given
        except AttributeError:
            return not_found_resp(
                f"Provider {str(provider)} (version {provider.version()}) has no "
                f"metric named '{metric_name}'"
            )
        # Catch all other cases
        except Exception as exc:  # pylint:disable=broad-except
            return bad_request_resp(f"Metric function returned an error: {str(exc)}")

        data = {metric_name: result}
        return ok_resp(data)


class MetricProviders(Resource):
    """
    BlueBird metric providers endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Returns a list of all the available metric providers
        :return:
        """

        data = {}
        for provider in metrics_providers():
            data.update({str(provider): provider.version()})

        return ok_resp(data)
