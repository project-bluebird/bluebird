"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, checked_resp
from bluebird.api.resources.utils.utils import parse_args, is_agent_mode, sim_proxy


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("filename", type=str, location="json", required=True)
_PARSER.add_argument("multiplier", type=float, location="json", required=False)


class Ic(Resource):
    """
    IC (initial condition) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. Loads the scenario contained in the given file
        :return:
        """

        req_args = parse_args(_PARSER)
        filename = req_args["filename"]

        if not filename:
            return bad_request_resp("No filename specified")

        multiplier = req_args["multiplier"]
        speed = multiplier if multiplier else 1.0

        if speed <= 0.0:
            return bad_request_resp(f"Invalid speed {speed}")

        err = sim_proxy().load_scenario(
            filename, speed=speed, start_paused=is_agent_mode()
        )

        return checked_resp(err)
