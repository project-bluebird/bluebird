"""
Provides logic for the DIRECT API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    CALLSIGN_LABEL,
    parse_args,
    bad_request_resp,
    sim_client,
    checked_resp,
)
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
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

        req_args = parse_args(_PARSER)
        waypoint = req_args["waypoint"]
        if not waypoint:
            return bad_request_resp("Waypoint name not specified")

        err = sim_client().direct_to_waypoint(req_args[CALLSIGN_LABEL], waypoint)

        return checked_resp(err)

