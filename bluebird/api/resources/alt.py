"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import internal_err_resp, RespTuple, ok_resp
from bluebird.api.resources.utils.utils import (
    CALLSIGN_LABEL,
    parse_args,
    check_callsign_exists,
    parse_route_data,
)
from bluebird.utils.types import Altitude, Callsign

# Parser for post requests
_PARSER_POST = reqparse.RequestParser()
_PARSER_POST.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
_PARSER_POST.add_argument("alt", type=Altitude, location="json", required=True)
_PARSER_POST.add_argument("vspd", type=int, location="json", required=False)

# Parser for get requests
_PARSER_GET = reqparse.RequestParser()
_PARSER_GET.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


# TODO Refactor this away using aircraft props
def _get_req_fl(callsign: Callsign):
    props = sim_client().get_aircraft_properties(callsign)

    if not props:
        return internal_err_resp(f"Could not get properties for {callsign}")

    fl_requested = None

    reply = None
    if reply and isinstance(reply, list):
        parsed_route = parse_route_data(reply)
        if isinstance(parsed_route, list):
            for part in parsed_route:
                if part["is_current"]:
                    fl_requested = part["req_alt"]

    return Altitude(fl_requested) if fl_requested else None


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

        err = sim_client().set_cleared_fl(
            callsign, fl_cleared, vspd=req_args.get("vspd")
        )
        if err:
            return internal_err_resp(err)

        # Record the cleared flight level
        # TODO This should be refactored to use {Callsign: Altitude} (in feet)
        ac_data().cleared_fls.update({str(callsign): fl_cleared.meters})

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

        err = check_callsign_exists(callsign)
        if err:
            return err

        # TODO Refactor ac_data so we don't need to manually str this
        callsign_str = str(callsign)

        # Current flight level
        # TODO Check units (from BlueSky) here - should be meters
        fl_current = Altitude(ac_data().get(callsign_str)[callsign_str]["alt"])

        # Cleared flight level
        # TODO Refactor cleared_fls to avoid manual None check
        fl_cleared = ac_data().cleared_fls.get(callsign_str)
        if fl_cleared:
            fl_cleared = Altitude(fl_cleared)

        # Requested flight level
        fl_requested = _get_req_fl(callsign)
        if isinstance(fl_requested, RespTuple):
            return fl_requested

        # If we don't know the requested flight level
        fl_requested_meters = fl_requested.meters if fl_requested else None

        data = {
            "fl_current": fl_current.meters,
            "fl_cleared": fl_cleared.meters,
            "fl_requested": fl_requested_meters,
        }

        return ok_resp(data)
