"""
Logic for metric endpoints
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app

PARSER = reqparse.RequestParser()
PARSER.add_argument("name", type=str, location="args", required=True)
PARSER.add_argument("args", type=str, location="args", required=False)
PARSER.add_argument("provider", type=str, location="args", required=False)

_LOGGER = logging.getLogger(__name__)


class Metric(Resource):
    """
    BlueBird Metric endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Attempts to call the method for the given metric
        :return: :class:`~flask.Response`
        """

        parsed = PARSER.parse_args()

        if not bb_app().metrics_providers:
            resp = jsonify("No metrics available")
            resp.status_code = 500
            return resp

        metric = parsed["name"]

        if parsed["provider"]:
            prov_name = parsed["provider"]
            provider = next(
                (x for x in bb_app().metrics_providers if str(x) == prov_name), None
            )
        else:
            provider = bb_app().metrics_providers[0]  # BlueBird's built-in metrics

        args = parsed["args"].split(",") if parsed["args"] else []

        try:

            result = provider(metric, *args)

        except AttributeError:

            resp = jsonify(
                f"Provider {str(provider)} (version {provider.version()}) has no metric named "
                f"'{metric}'"
            )
            resp.status_code = 404
            return resp

        except (TypeError, AssertionError) as exc:

            resp = jsonify(f"Invalid arguments for metric function: {str(exc)}")
            resp.status_code = 400
            return resp

        resp = jsonify({metric: result})
        resp.status_code = 200
        return resp


class MetricProviders(Resource):
    """
    BlueBird metric providers endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Returns a list of all the available metric providers
        :return: :class:`~flask.Response`
        """

        data = {}
        for provider in bb_app().metrics_providers:
            data.update({str(provider): provider.version()})

        return jsonify(data)
