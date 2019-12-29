"""
Provides logic for the DIRECT API endpoint
"""

# TODO Could also specify a target altitude here

from flask_restful import Resource, reqparse

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
        Logic for POST events. If the request contains an existing aircraft ID and valid
        waypoint name, then a request is sent to the aircraft to head directly to the
        waypoint
        """

        req_args = utils.parse_args(_PARSER)
        waypoint_str = req_args["waypoint"]

        if not waypoint_str:
            return responses.bad_request_resp("Waypoint name must be specified")

        waypoint = utils.sim_proxy().waypoints.find(waypoint_str)
        if not waypoint:
            return responses.bad_request_resp(f"Could not find waypoint {waypoint_str}")

        callsign = req_args[utils.CALLSIGN_LABEL]

        resp = utils.check_exists(callsign)
        if resp:
            return resp

        err = utils.sim_proxy().aircraft.direct_to_waypoint(callsign, waypoint)

        return responses.checked_resp(err)
