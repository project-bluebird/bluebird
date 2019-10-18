"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import (
    bad_request_resp,
    checked_resp,
    ok_resp,
)
from bluebird.api.resources.utils.utils import CALLSIGN_LABEL, parse_args, sim_proxy
from bluebird.utils.types import Altitude, Callsign

# Parser for post requests
_PARSER_POST = reqparse.RequestParser()
_PARSER_POST.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
# TODO Update API.md and make all type args match their __init__ options (i.e. str or int here)
_PARSER_POST.add_argument("alt", type=Altitude, location="json", required=True)
_PARSER_POST.add_argument("vspd", type=int, location="json", required=False)

# Parser for get requests
_PARSER_GET = reqparse.RequestParser()
_PARSER_GET.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


class Alt(Resource):
    """
    ALT (altitude) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its altitude.
        :return:
        """

        req_args = parse_args(_PARSER_POST)
        callsign: Callsign = req_args[CALLSIGN_LABEL]
        fl_cleared: Altitude = req_args["alt"]

        err = sim_proxy().set_cleared_fl(
            callsign, fl_cleared, vspd=req_args.get("vspd")
        )

        return checked_resp(err)

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing
        aircraft, then its current, requested, and cleared flight levels are returned
        (if they can be determined)
        :return:
        """

        req_args = parse_args(_PARSER_GET)
        callsign = req_args[CALLSIGN_LABEL]

        aircraft_props, _ = sim_proxy().get_aircraft_props(callsign)

        if not aircraft_props:
            return bad_request_resp(f"Aircraft {callsign} not found")

        # TODO Check units (from BlueSky) - should be meters, but have changed to feet here
        data = {
            callsign.value: {
                "fl_current": aircraft_props.altitude.feet,
                "fl_cleared": aircraft_props.cleared_flight_level.feet,
                "fl_requested": aircraft_props.requested_flight_level.feet,
            }
        }

        return ok_resp(data)
