"""
Logic for metric endpoints
"""
# TODO(RKM 2019-11-23) Should add a flag to assert that the sim has advanced (has been
# stepped) since the previous call to the metric endpoint
import logging
import traceback

from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="args", required=True)
_PARSER.add_argument("args", type=str, location="args", required=False)
_PARSER.add_argument("provider", type=str, location="args", required=False)

_LOGGER = logging.getLogger(__name__)


class Metric(Resource):
    """BlueBird Metrics endpoint"""

    @staticmethod
    def get():
        """Logic for GET events. Attempts to call the method for the given metric"""

        if not utils.sim_proxy().metrics_providers:
            return responses.internal_err_resp("No metrics available")

        req_args = utils.parse_args(_PARSER)
        metric_name = req_args["name"]

        if not metric_name:
            return responses.bad_request_resp("Metric name must be specified")

        # Use the default metrics if not otherwise specified
        provider_name = req_args["provider"] if req_args["provider"] else "BlueBird"
        provider = utils.sim_proxy().metrics_providers.get(provider_name)
        if not provider:
            return responses.bad_request_resp(f'Provider "{provider_name}" not found')

        args = req_args["args"].split(",") if req_args["args"] else []

        try:
            result = utils.sim_proxy().call_metric_function(provider, metric_name, args)
        except AttributeError:  # Catch cases where a wrong metric name is given
            return responses.not_found_resp(
                f"Provider {str(provider)} (version {provider.version()}) has no "
                f"metric named '{metric_name}'"
            )
        except Exception as exc:  # Catch all other cases
            return responses.bad_request_resp(
                f"Metric function returned an error: {exc}\n{traceback.format_exc()}"
            )

        if isinstance(result, str):
            return responses.internal_err_resp(result)

        return responses.ok_resp({metric_name: result})


class MetricProviders(Resource):
    """BlueBird metric providers endpoint"""

    @staticmethod
    def get():
        """Logic for GET events. Returns a list of all the available metric providers"""

        data = {}
        for provider in utils.sim_proxy().metrics_providers:
            data.update({str(provider): provider.version()})

        return responses.ok_resp(data)
