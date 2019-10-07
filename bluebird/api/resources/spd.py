"""
Provides logic for the SPD (set ground speed) API endpoint
"""

# TODO Check which speed we should specify here

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import checked_resp, bad_request_resp
from bluebird.api.resources.utils.utils import (
    parse_args,
    CALLSIGN_LABEL,
    sim_client,
    sim_proxy,
)
from bluebird.utils.types import Callsign, GroundSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
_PARSER.add_argument("spd", type=GroundSpeed, location="json", required=True)


class Spd(Resource):
    """
    Contains logic for the SPD endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its horizontal speed
        :return:
        """

        req_args = parse_args(_PARSER)

        callsign = req_args[CALLSIGN_LABEL]
        if not sim_proxy().contains(callsign):
            return bad_request_resp(f"Aircraft {callsign} was not found")

        err = sim_client().aircraft.set_ground_speed(callsign, req_args["spd"])

        return checked_resp(err)
