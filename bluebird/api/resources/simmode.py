"""
Provides logic for the SIM MODE API endpoint
"""

import logging

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.utils import parse_args, sim_proxy
from bluebird.settings import Settings

# NOTE: Module name clashes with the API class name below
from bluebird.utils.properties import SimMode as _SimMode


_LOGGER = logging.getLogger(__name__)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("mode", type=str, location="json", required=True)


class SimMode(Resource):
    """Logic for the SimMode endpoint"""

    @staticmethod
    def post():
        """Logic for POST events. Changes the simulation mode"""

        req_args = parse_args(_PARSER)
        new_mode_str = req_args["mode"]

        try:
            new_mode = _SimMode(new_mode_str)
        except ValueError:
            return responses.bad_request_resp(
                f'Mode "{new_mode_str}" not supported. Must be one of: '
                f'{", ".join([x.name for x in _SimMode])}'
            )

        if Settings.SIM_MODE == new_mode:
            return responses.ok_resp(f"Already in {new_mode.name} mode!")

        _LOGGER.info(f"Setting mode to {new_mode.name}")

        err = sim_proxy().set_mode(new_mode)

        return responses.checked_resp(err)
