"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.settings import Settings
from bluebird.utils.properties import SimMode
from bluebird.api.resources.utils import (
    check_ac_data_populated,
    sim_client,
    parse_args,
    bad_request_resp,
    internal_err_resp,
    checked_resp,
)

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

        parsed = parse_args(_PARSER)
        filename = fn_base = parsed["filename"]

        if not filename:
            return bad_request_resp("No filename specified")

        # TODO Handle this in BlueSky sim_client
        # if not filename.lower().endswith(".scn"):
        #     filename += ".scn"

        multiplier = parsed["multiplier"]
        speed = multiplier if multiplier else 1.0

        if speed <= 0.0:
            return bad_request_resp(f"Invalid speed {speed}")

        start_paused = Settings.SIM_MODE == SimMode.Agent
        err = sim_client().load_scenario(
            filename, speed=speed, start_paused=start_paused
        )

        if err:
            return internal_err_resp(
                f"Error: Could not load scenario {fn_base}. Error was: {err}"
            )

        err = check_ac_data_populated()

        return checked_resp(err)
