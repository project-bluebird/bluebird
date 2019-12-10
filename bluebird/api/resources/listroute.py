"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.utils import CALLSIGN_LABEL, parse_args, sim_proxy
from bluebird.utils.properties import AircraftRoute
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


class ListRoute(Resource):
    """
    Contains logic for the LISTROUTE endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing
        aircraft, then information about its route (FMS flightplan) is returned
        :return:
        """

        req_args = parse_args(_PARSER)
        callsign = req_args[CALLSIGN_LABEL]

        resp = utils.check_exists(callsign)
        if resp:
            return resp

        route = sim_proxy().aircraft.route(callsign)
        assert route, "No route returned even though the aircraft exists"
        if not isinstance(route, AircraftRoute):
            return responses.internal_err_resp(route)

        data = utils.convert_aircraft_route(route)
        return responses.ok_resp(data)
