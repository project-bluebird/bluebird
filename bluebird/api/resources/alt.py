"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import AircraftProperties
from bluebird.utils.types import Altitude, Callsign, VerticalSpeed

# Parser for post requests
_PARSER_POST = reqparse.RequestParser()
_PARSER_POST.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
# TODO Update API.md and make all type args match their __init__ options (i.e. str or
# int here)
_PARSER_POST.add_argument("alt", type=Altitude, location="json", required=True)
_PARSER_POST.add_argument("vspd", type=VerticalSpeed, location="json", required=False)

# Parser for get requests
_PARSER_GET = reqparse.RequestParser()
_PARSER_GET.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="args", required=True
)


class Alt(Resource):
    """ALT (altitude) command"""

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its altitude
        """

        req_args = utils.parse_args(_PARSER_POST)
        callsign: Callsign = req_args[utils.CALLSIGN_LABEL]
        fl_cleared: Altitude = req_args["alt"]

        err = utils.sim_proxy().aircraft.set_cleared_fl(
            callsign, fl_cleared, vspd=req_args.get("vspd")
        )

        return responses.checked_resp(err)

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing
        aircraft, then its current, requested, and cleared flight levels are returned
        (if they can be determined)
        """

        req_args = utils.parse_args(_PARSER_GET)
        callsign = req_args[utils.CALLSIGN_LABEL]

        resp = utils.check_exists(callsign)
        if resp:
            return resp

        aircraft_props = utils.sim_proxy().aircraft.get_properties(callsign)

        if not isinstance(aircraft_props, AircraftProperties):
            return responses.internal_err_resp(
                f"Couldn't get properties for {callsign}: {aircraft_props}"
            )

        # TODO Check units (from BlueSky) - should be meters, but have changed to feet
        # here
        data = {
            callsign.value: {
                "fl_current": aircraft_props.altitude.feet,
                "fl_cleared": aircraft_props.cleared_flight_level.feet,
                "fl_requested": aircraft_props.requested_flight_level.feet,
            }
        }

        return responses.ok_resp(data)
