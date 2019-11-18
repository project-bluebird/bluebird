"""
Provides logic for the VS (vertical speed) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import checked_resp
from bluebird.api.resources.utils.utils import CALLSIGN_LABEL, parse_args, sim_proxy
from bluebird.utils.types import Callsign, VerticalSpeed


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)
_PARSER.add_argument("vspd", type=VerticalSpeed, location="args", required=True)


# TODO Is this used at all? Seems more likely that users will just want to set cleared
# flight levels
class Vs(Resource):
    """
    Contains logic for the VS endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft callsign,
        then a request is sent to alter its vertical speed
        :return:
        """

        req_args = parse_args(_PARSER)

        err = sim_proxy().aircraft.set_vertical_speed(
            req_args[CALLSIGN_LABEL], req_args["vspd"]
        )

        return checked_resp(err)
