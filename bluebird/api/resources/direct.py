"""
Provides logic for the DIRECT API endpoint
"""

# TODO Could also specify a target altitude here

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, ok_resp
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("waypoint", type=str, location="json", required=True)


class Direct(Resource):
    """
    Contains logic for the DIRECT endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to move directly to the specified waypoint. The specified
        waypoint must exist on the aircraft's route
        :return:
        """

        req_args = utils.parse_args(_PARSER)
        waypoint = req_args["waypoint"]

        if not waypoint:
            return bad_request_resp("Waypoint name not specified")

        callsign = req_args[utils.CALLSIGN_LABEL]

        if not utils.sim_proxy().contains(callsign):
            return bad_request_resp(f"Aircraft {callsign} was not found")

        err = utils.sim_client().aircraft.direct_to_waypoint(callsign, waypoint)

        return bad_request_resp(err) if err else ok_resp()
