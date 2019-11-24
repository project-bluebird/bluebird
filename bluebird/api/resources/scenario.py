"""
Provides logic for the scenario (create scenario) API endpoint
"""

from http import HTTPStatus
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.scenario_validation import validate_geojson_scenario
from bluebird.api.resources.utils.utils import sim_proxy, parse_args


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("scenario_name", type=str, location="json", required=True)
_PARSER.add_argument(
    "content", type=str, action="append", location="json", required=True
)


class Scenario(Resource):
    """Contains logic for the scenario endpoint"""

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = parse_args(_PARSER)

        scn_name = req_args["scn_name"]

        # TODO The BlueSky client needs to handle the various "scenario/*[.scn]" options
        # now

        if not scn_name:
            return responses.bad_request_resp("Scenario name must be provided")

        content = req_args["content"]

        err = validate_geojson_scenario(content)
        if err:
            return responses.bad_request_resp(f"Invalid scenario content: {err}")

        err = sim_proxy().simulation.upload_new_scenario(scn_name, content)

        return responses.checked_resp(err, HTTPStatus.CREATED)
