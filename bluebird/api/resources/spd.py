"""
Provides logic for the SPD (set ground speed) API endpoint
"""

# TODO(RKM 2019-11-18) Check which speed we should specify here. Maybe change to "gspd"
# for clarity

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import checked_resp
from bluebird.utils.types import Callsign, GroundSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
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

        req_args = utils.parse_args(_PARSER)

        callsign = req_args[utils.CALLSIGN_LABEL]
        resp = utils.check_exists(callsign)
        if resp:
            return resp

        err = utils.sim_proxy().aircraft.set_ground_speed(callsign, req_args["spd"])

        return checked_resp(err)
