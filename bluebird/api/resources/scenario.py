"""
Provides logic for the scenario endpoint
"""

from http import HTTPStatus
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.scenario_validation import validate_json_scenario


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="json", required=True)
_PARSER.add_argument("content", type=dict, location="json", required=True)


class Scenario(Resource):
    """Contains logic for the scenario endpoint"""

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = utils.parse_args(_PARSER)

        if not utils.sim_proxy().sector:
            return responses.bad_request_resp(
                "A sector definition is required before uploading a scenario"
            )

        scn_name = req_args["name"]
        if not scn_name:
            return responses.bad_request_resp("Scenario name must be provided")

        content = req_args["content"]

        err = validate_json_scenario(content)
        if err:
            return responses.bad_request_resp(f"Invalid scenario content: {err}")

        err = utils.sim_proxy().simulation.upload_new_scenario(scn_name, content)

        return responses.checked_resp(err, HTTPStatus.CREATED)
