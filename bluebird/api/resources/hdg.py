"""
Provides logic for the HDG (heading) API endpoint
"""
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign
from bluebird.utils.types import Heading


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="json", required=True
)
_PARSER.add_argument("hdg", type=Heading, location="json", required=True)


class Hdg(Resource):
    """Contains logic for the HDG endpoint"""

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a
        request is sent to alter its heading
        """

        req_args = utils.parse_args(_PARSER)

        callsign = req_args[utils.CALLSIGN_LABEL]
        resp = utils.check_exists(utils.sim_proxy(), callsign)
        if resp:
            return resp

        heading = req_args["hdg"]

        err = utils.sim_proxy().aircraft.set_heading(callsign, heading)

        return responses.checked_resp(err)
