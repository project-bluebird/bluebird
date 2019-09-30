"""
Provides logic for the HDG (heading) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    CALLSIGN_LABEL,
    parse_args,
    sim_client,
    checked_resp,
)
from bluebird.utils.types import Callsign, Heading


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="json", required=True)
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

        parsed = parse_args(_PARSER)

        err = sim_client().set_heading(parsed["callsign"], parsed["heading"])

        return checked_resp(err)
