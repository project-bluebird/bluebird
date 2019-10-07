"""
Provides logic for the SIM MODE API endpoint
"""

import logging

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.utils import parse_args, is_agent_mode, sim_proxy
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode as SimMode_prop


_LOGGER = logging.getLogger(__name__)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("mode", type=str, location="json", required=True)


class SimMode(Resource):
    """
    Logic for the SimMode endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. Changes the simulation mode
        :return:
        """

        req_args = parse_args(_PARSER)
        new_mode = req_args["mode"]

        try:
            Settings.set_sim_mode(new_mode)
        except ValueError:
            return responses.bad_request_resp(
                f'Mode "{new_mode}"" not supported. Must be one of: '
                f'{", ".join([x.name for x in SimMode_prop])}'
            )

        _LOGGER.debug(f"Mode set to {new_mode}")

        if is_agent_mode():
            err = sim_proxy().pause_sim()
            if err:
                return responses.internal_err_resp(
                    f"Could not pause sim when changing mode: {err}"
                )

        elif Settings.SIM_MODE == SimMode_prop.Sandbox:
            err = sim_proxy().resume_sim()
            if err:
                return responses.internal_err_resp(
                    f"Could not resume sim when changing mode: {err}"
                )
        else:
            # Only reach here if we add a new mode to settings but don't add a case to
            # handle it here
            raise ValueError(f"Unsupported mode {Settings.SIM_MODE}")

        return responses.ok_resp()
