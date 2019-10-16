"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import (
    bad_request_resp,
    checked_resp,
    ok_resp,
    internal_err_resp,
)
from bluebird.api.resources.utils.utils import parse_args, sim_client, sim_proxy
from bluebird.settings import is_agent_mode


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("filename", type=str, location="json", required=True)
_PARSER.add_argument("multiplier", type=float, location="json", required=False)


class Ic(Resource):
    """
    IC (initial condition) command
    """

    # TODO Update API.md
    @staticmethod
    def get():
        """
        Gets the current scenario (file)name
        """

        scn_name = sim_client().simulation.scenario_name

        return (
            ok_resp({"scn_name": scn_name})
            if isinstance(scn_name, str)
            else internal_err_resp(str(scn_name))
        )

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
