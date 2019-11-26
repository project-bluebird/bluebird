"""
Logic for metric endpoints
"""

# TODO(RKM 2019-11-23) Should add a flag to assert that the sim has advanced (has been
# stepped) since the previous call to the metric endpoint

import logging
import traceback

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.utils import metrics_providers, parse_args


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="args", required=True)
_PARSER.add_argument("args", type=str, location="args", required=False)
_PARSER.add_argument("provider", type=str, location="args", required=False)

_LOGGER = logging.getLogger(__name__)


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
            return responses.internal_err_resp("No metrics available")

        req_args = parse_args(_PARSER)
        metric_name = req_args["name"]

        if not metric_name:
            return responses.bad_request_resp("Metric name must be specified")

        # Use the default metrics if not otherwise specified
        provider = metrics_providers().get("BlueBird")

        req_provider = req_args["provider"]
        if req_provider:
            provider = metrics_providers().get(req_provider)
            if not provider:
                responses.bad_request_resp(f'Provider "{req_provider}" not found')

        args = req_args["args"].split(",") if req_args["args"] else []

        try:
            result = provider(metric_name, *args)
        # Catch cases where a wrong metric name is given
        except AttributeError:
            return responses.not_found_resp(
                f"Provider {str(provider)} (version {provider.version()}) has no "
                f"metric named '{metric_name}'"
            )
        # Catch all other cases
        except Exception:
            return responses.bad_request_resp(
                f"Metric function returned an error: {traceback.format_exc()}"
            )

        return (
            responses.ok_resp({metric_name: result})
            if not isinstance(result, str)
            else responses.internal_err_resp(result)
        )


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
        for provider in metrics_providers().providers:
            data.update({str(provider): provider.version()})

        return responses.ok_resp(data)
