"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

import logging

import re
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    sim_client,
    CALLSIGN_LABEL,
    internal_err_resp,
    parse_args,
    check_callsign_exists,
)
from bluebird.utils.types import Callsign

_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)

_LOGGER = logging.getLogger(__name__)

_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


# TODO Move to the BlueSky client utils
def parse_route_data(route_data):
    """
    Parse a list of strings containing route data into a keyed dictionary
    :param route_data:
    :return:
    """

    parsed = []
    for line in map(lambda s: s.replace(" ", ""), route_data):
        match = _ROUTE_RE.match(line)
        if not match:
            return line
        req_alt = match.group(3) if not "-" in match.group(3) else None
        req_spd = int(match.group(4)) if not "-" in match.group(4) else None
        parsed.append(
            {
                "is_current": bool(match.group(1)),
                "wpt_name": match.group(2),
                "req_alt": req_alt,
                "req_spd": req_spd,
            }
        )
    return parsed


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
