"""
Provides logic for the DTMULT API endpoint
"""
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("multiplier", type=float, location="json", required=True)


class DtMult(Resource):
    """DTMULT command"""

    @staticmethod
    def post():
        """Logic for POST events. Sets the speed multiplier for the simulation"""

        req_args = utils.parse_args(_PARSER)
        multiplier = round(req_args["multiplier"], 2)

        if multiplier <= 0:
            return responses.bad_request_resp("Multiplier must be greater than 0")

        # TODO Check if we still need to keep track of step_dt in the client
        err = utils.sim_proxy().simulation.set_speed(multiplier)

        return responses.checked_resp(err)
