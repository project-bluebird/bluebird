"""
Logic for the set ground speed API endpoint
"""
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import checked_resp
from bluebird.utils.types import Callsign
from bluebird.utils.types import GroundSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("gspd", type=GroundSpeed, location="json", required=True)


class Gspd(Resource):
    """Contains logic for the SPD endpoint"""

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its ground speed
        """

        req_args = utils.parse_args(_PARSER)

        callsign = req_args[utils.CALLSIGN_LABEL]
        resp = utils.check_exists(utils.sim_proxy(), callsign)
        if resp:
            return resp

        err = utils.sim_proxy().aircraft.set_ground_speed(callsign, req_args["gspd"])

        return checked_resp(err)
