"""
Provides logic for the CRE (create aircraft) API endpoint
"""

from http import HTTPStatus

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, checked_resp
from bluebird.api.resources.utils.utils import (
    CALLSIGN_LABEL,
    try_parse_lat_lon,
    parse_args,
)
from bluebird.utils.types import Callsign, Altitude, LatLon, Heading, GroundSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
_PARSER.add_argument("type", type=str, location="json", required=True)
_PARSER.add_argument("lat", type=float, location="json", required=True)
_PARSER.add_argument("lon", type=float, location="json", required=True)
_PARSER.add_argument("hdg", type=Heading, location="json", required=True)
_PARSER.add_argument("alt", type=Altitude, location="json", required=True)
_PARSER.add_argument("spd", type=GroundSpeed, location="json", required=True)


class Cre(Resource):
    """
    CRE (create aircraft) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains valid aircraft information, then
        a request is sent to the simulator to create it
        :return:
        """

        req_args = parse_args(_PARSER)
        callsign = req_args[CALLSIGN_LABEL]

        # TODO Replace ac_data keys with callsigns (also need to parse callsigns coming
        # from the simulators)
        if ac_data().contains(str(callsign)):
            return bad_request_resp(f"Aircraft {callsign} already exists")

        position = try_parse_lat_lon(req_args)
        if not isinstance(position, LatLon):
            return position

        if req_args["spd"] <= 0:
            return bad_request_resp("Speed must be positive")

        err = sim_client().create_aircraft(
            callsign, position, req_args["hdg"], req_args["alt"], req_args["spd"]
        )

        return checked_resp(err, HTTPStatus.CREATED)
