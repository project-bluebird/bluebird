"""
Provides logic for the CRE (create aircraft) API endpoint
"""

from http import HTTPStatus

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, checked_resp
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign, Altitude, LatLon, Heading, GroundSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("type", type=str, location="json", required=True)
_PARSER.add_argument("lat", type=float, location="json", required=True)
_PARSER.add_argument("lon", type=float, location="json", required=True)
_PARSER.add_argument("hdg", type=Heading, location="json", required=True)
_PARSER.add_argument("alt", type=Altitude, location="json", required=True)
_PARSER.add_argument("gspd", type=GroundSpeed, location="json", required=True)


class Cre(Resource):
    """
    CRE (create aircraft) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains valid aircraft information, then
        a request is sent to the simulator to create it
        """

        req_args = utils.parse_args(_PARSER)
        callsign = req_args[utils.CALLSIGN_LABEL]

        resp = utils.check_exists(callsign, negate=True)
        if resp:
            return resp

        position_or_resp = utils.try_parse_lat_lon(req_args)
        if not isinstance(position_or_resp, LatLon):
            return position_or_resp

        if req_args["gspd"].meters_per_sec <= 0:
            return bad_request_resp("Speed must be positive")

        if not req_args["type"]:
            return bad_request_resp("Aircraft type must be specified")

        err = utils.sim_proxy().aircraft.create(
            callsign,
            req_args["type"],
            position_or_resp,
            req_args["hdg"],
            req_args["alt"],
            req_args["gspd"],
        )

        return checked_resp(err, HTTPStatus.CREATED)
