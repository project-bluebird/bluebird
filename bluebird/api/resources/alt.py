"""
Provides logic for the ALT (altitude) API endpoint
"""
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Altitude
from bluebird.utils.types import Callsign
from bluebird.utils.types import VerticalSpeed

# Parser for post requests
_PARSER_POST = reqparse.RequestParser()
_PARSER_POST.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
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
