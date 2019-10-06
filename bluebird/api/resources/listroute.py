"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

import logging

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import internal_err_resp
from bluebird.api.resources.utils.utils import (
    CALLSIGN_LABEL,
    parse_args,
    check_callsign_exists,
)
from bluebird.utils.types import Callsign


_LOGGER = logging.getLogger(__name__)

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

        parsed = parse_args(_PARSER)
        callsign = parsed[CALLSIGN_LABEL]

        err = check_callsign_exists(callsign)
        if err:
            return err

        # TODO Response expected from BlueSky sim
        props = sim_client().get_aircraft_properties(callsign)
        if not props:
            return internal_err_resp(f"Could not get properties for {callsign}")

        # TODO Refactor this - should get a standard set of properties back
        reply = None
        if not reply:
            return internal_err_resp("Not implemented")
