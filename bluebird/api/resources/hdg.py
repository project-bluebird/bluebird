"""
Provides logic for the HDG (heading) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import checked_resp, bad_request_resp
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign, Heading


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("hdg", type=Heading, location="json", required=True)


class Hdg(Resource):
    """
    Contains logic for the HDG endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its heading
        :return:
        """

        req_args = utils.parse_args(_PARSER)

        callsign = req_args[utils.CALLSIGN_LABEL]

        if not utils.sim_proxy().contains(callsign):
            return bad_request_resp(f"Aircraft {callsign} was not found")

        heading = req_args["hdg"]
        err = utils.sim_client().aircraft.set_heading(callsign, heading)

        return checked_resp(err)
