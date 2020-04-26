"""
Provides logic for the DIRECT API endpoint
"""
# TODO Could also specify a target altitude here
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("waypoint", type=str, location="json", required=True)


class Direct(Resource):
    """Contains logic for the DIRECT endpoint"""

    @staticmethod
    def post():
        """
        Requests that the specified aircraft proceeds immediately to the specified
        waypoint
        """

        req_args = utils.parse_args(_PARSER)
        waypoint_name = req_args["waypoint"]

        if not waypoint_name:
            return responses.bad_request_resp("Waypoint name must be specified")

        callsign = req_args[utils.CALLSIGN_LABEL]

        resp = utils.check_exists(utils.sim_proxy(), callsign)
        if resp:
            return resp

        err = utils.sim_proxy().aircraft.direct_to_waypoint(callsign, waypoint_name)

        return responses.checked_resp(err)
