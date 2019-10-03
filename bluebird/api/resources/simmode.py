"""
Provides logic for the SIM MODE API endpoint
"""

import logging

from flask_restful import Resource, reqparse

from bluebird.settings import Settings
from bluebird.utils.properties import SimMode as SimMode_prop
from bluebird.api.resources.utils import (
    ac_data,
    sim_client,
    parse_args,
    bad_request_resp,
    internal_err_resp,
    ok_resp,
)

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
            return bad_request_resp(
                f'Mode "{new_mode}"" not supported. Must be one of: '
                f'{", ".join([x.name for x in SimMode_prop])}'
            )

        _LOGGER.debug(f"Mode set to {new_mode}")

        if Settings.SIM_MODE == SimMode_prop.Agent:
            ac_data().set_log_rate(0)
            err = sim_client().pause_sim()
            if err:
                return internal_err_resp(
                    f"Could not pause sim when changing mode: {err}"
                )

        elif Settings.SIM_MODE == SimMode_prop.Sandbox:
            ac_data().resume_log()
            err = sim_client().resume_sim()
            if err:
                return internal_err_resp(
                    f"Could not resume sim when changing mode: {err}"
                )
        else:
            # Only reach here if we add a new mode to settings but don't add a case to
            # handle it here
            raise ValueError(f"Unsupported mode {Settings.SIM_MODE}")

        return ok_resp()
