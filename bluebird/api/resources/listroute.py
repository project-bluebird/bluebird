"""
Provides logic for the LISTROUTE (list route) API endpoint
"""
# NOTE(RKM 2019-11-19) Only the waypoint names are currently returned. Do we want to
# (optionally) also return their full lat/lon?
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="args", required=True
)


class ListRoute(Resource):
    """Contains logic for the LISTROUTE endpoint"""

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing
        aircraft, then information about its route (FMS flightplan) is returned
        """

        req_args = utils.parse_args(_PARSER)
        callsign = req_args[utils.CALLSIGN_LABEL]

        resp = utils.check_exists(utils.sim_proxy(), callsign)
        if resp:
            return resp

        route_info = utils.sim_proxy().aircraft.route(callsign)

        if not isinstance(route_info, tuple):
            if route_info == "Aircraft has no route":
                return responses.bad_request_resp(route_info)
            return responses.internal_err_resp(route_info)

        data = {
            utils.CALLSIGN_LABEL: str(callsign),
            "route_name": route_info[0],
            "next_waypoint": route_info[1],
            "route_waypoints": route_info[2],
        }
        return responses.ok_resp(data)
