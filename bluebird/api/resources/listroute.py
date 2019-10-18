"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

import logging

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import (
    internal_err_resp,
    ok_resp,
    bad_request_resp,
)
from bluebird.api.resources.utils.utils import CALLSIGN_LABEL, parse_args, sim_proxy
from bluebird.utils.types import Callsign


_LOGGER = logging.getLogger(__name__)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


# req_args = parse_args(_PARSER)
# callsign = req_args[CALLSIGN_LABEL]


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

        if not sim_proxy().contains(callsign):
            return bad_request_resp(f"Aircraft {callsign} was not found")

        route = sim_proxy().get_aircraft_route(callsign)
        if isinstance(route, str):
            return internal_err_resp(route)

        return ok_resp({CALLSIGN_LABEL: callsign.value, "route": route})

