"""
Provides logic for the POS (position) API endpoint
"""


from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    ac_data,
    CALLSIGN_LABEL,
    parse_args,
    bad_request_resp,
    check_callsign_exists,
    ok_resp,
)
from bluebird.utils.types import Callsign

_PARSER = reqparse.RequestParser()
# TODO This needs changed to accept multiple (comma-separated) callsigns again
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


class Pos(Resource):
    """
    BlueSky POS (position) command
    """

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing aircraft,
        then information about that aircraft is returned.
        :return:
        """

        req_args = parse_args(_PARSER)
        callsign = req_args[CALLSIGN_LABEL]

        # TODO If we aren't streaming the ac data then we need to handle this differently
        if str(callsign).upper() == "ALL":
            if not ac_data().store:
                return bad_request_resp("No aircraft in the simulation")
        else:
            err = check_callsign_exists(callsign)
            if err:
                return err

        data = ac_data().get(str(callsign))
        return ok_resp(data)
