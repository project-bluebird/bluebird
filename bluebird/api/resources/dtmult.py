"""
Provides logic for the DTMULT API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    ac_data,
    sim_client,
    parse_args,
    bad_request_resp,
    checked_resp,
)


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("multiplier", type=float, location="json", required=True)


class DtMult(Resource):
    """
    DTMULT command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. Sets the speed multiplier for the simulation
        :return:
        """

        req_args = parse_args(_PARSER)
        multiplier = round(req_args["multiplier"], 2)

        if multiplier <= 0:
            return bad_request_resp("Multiplier must be greater than 0")

        # TODO Check if we still need to keep track of step_dt in the client
        err = sim_client().set_sim_speed(multiplier)

        resp = checked_resp(err)

        if err:
            return resp

        ac_data().set_log_rate(multiplier)
        return resp
