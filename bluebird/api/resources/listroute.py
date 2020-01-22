"""
Provides logic for the LISTROUTE (list route) API endpoint
"""
from typing import Any
from typing import Dict

from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import AircraftRoute
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="args", required=True
)


# NOTE(RKM 2019-11-19) Only the waypoint names are currently returned. Do we want to
# (optionally) also return their full lat/lon?
def _convert_aircraft_route(route: AircraftRoute) -> Dict[str, Any]:
    """Parses an AircraftRoute object into a dict suitable for returning via Flask"""

    data = {
        "route": [],
        "current_segment_index": route.current_segment_index,
    }

    for segment in route.segments:
        data["route"].append(
            {
                "wpt_name": segment.waypoint.name,
                "req_alt": (
                    segment.waypoint.altitude.feet
                    if segment.waypoint.altitude
                    else None
                ),
                "req_gspd": (
                    segment.required_gspd.feet_per_sec
                    if segment.required_gspd
                    else None
                ),
            }
        )

    return data


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
            if route == "Aircraft has no route":
                return responses.bad_request_resp(route)
            return responses.internal_err_resp(route)

        data = {
            utils.CALLSIGN_LABEL: str(callsign),
            **_convert_aircraft_route(route),
        }
        return responses.ok_resp(data)
