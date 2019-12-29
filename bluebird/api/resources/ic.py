"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimProperties, SimMode


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("filename", type=str, location="json", required=True)
_PARSER.add_argument("multiplier", type=float, location="json", required=False)


class Ic(Resource):
    """IC (initial condition) command"""

    @staticmethod
    def get():
        """Gets the current scenario name"""

        props = utils.sim_proxy().simulation.properties
        if not isinstance(props, SimProperties):
            return responses.internal_err_resp(f"Couldn't get sim properties: {props}")

        data = {"scenario_name": props.scenario_name}
        return responses.ok_resp(data)

    @staticmethod
    def post():
        """Logic for POST events. Loads the scenario contained in the given file"""

        req_args = utils.parse_args(_PARSER)
        filename = req_args["filename"]

        if not filename:
            return responses.bad_request_resp("No filename specified")

        multiplier = req_args["multiplier"]
        speed = multiplier if multiplier else 1.0

        if speed <= 0.0:
            return responses.bad_request_resp(f"Invalid speed {speed}")

        err = utils.sim_proxy().simulation.load_scenario(
            filename, speed=speed, start_paused=(Settings.SIM_MODE == SimMode.Agent)
        )

        return responses.checked_resp(err)
