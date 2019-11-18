"""
Provides logic for the ADDWPT (add waypoint to route) API endpoint

TODO: Consider renaming this since its meaning can be confusing
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.utils as utils
import bluebird.api.resources.utils.responses as responses
import bluebird.utils.types as types


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=types.Callsign, location="json", required=True
)
_PARSER.add_argument("waypoint", type=str, location="json", required=True)
_PARSER.add_argument("alt", type=types.Altitude, location="json", required=False)
_PARSER.add_argument("spd", type=float, location="json", required=False)


class AddWpt(Resource):
    """
    BlueSky ADDWPT (add waypoint to route) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request is valid, then the specified waypoint is
        added to the aircraft's route
        :return:
        """

        req_args = utils.parse_args(_PARSER)
        callsign: types.Callsign = req_args[utils.CALLSIGN_LABEL]

        waypoint_str = req_args["waypoint"]
        if not waypoint_str:
            return responses.bad_request_resp("A waypoint name must be provided")

        resp = utils.check_exists(callsign)
        if resp:
            return resp

        waypoint = utils.sim_proxy().waypoints.find(waypoint_str)
        if not waypoint:
            return responses.bad_request_resp(f"Could not find waypoint {waypoint_str}")

        # TODO Which speed is this? Ground speed?
        err = utils.sim_proxy().aircraft.add_waypoint_to_route(
            callsign, waypoint, spd=req_args["spd"]
        )

        return responses.checked_resp(err)
