"""
Provides logic for the SPD (_ speed) API endpoint
"""

# TODO Which speed are we specifying here?

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    parse_args,
    checked_resp,
    CALLSIGN_LABEL,
    bad_request_resp,
    sim_client,
)
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
_PARSER.add_argument("spd", type=int, location="json", required=True)


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
        speed: int = req_args["spd"]

        if speed <= 0:
            return bad_request_resp("Speed must be positive")

        err = sim_client().set_aircraft_speed(speed)

        return checked_resp(err)
