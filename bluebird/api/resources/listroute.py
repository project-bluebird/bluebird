"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import AircraftRoute
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

        route = utils.sim_proxy().aircraft.route(callsign)

        if not isinstance(route, AircraftRoute):
            return responses.internal_err_resp(route)

        data = utils.convert_aircraft_route(route)
        return responses.ok_resp(data)
