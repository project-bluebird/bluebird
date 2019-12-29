"""
Provides logic for the SEED (set seed) API endpoint
"""

from bluebird.utils.types import is_valid_seed
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("value", type=int, location="json", required=True)


class Seed(Resource):
    """SEED (set seed) command"""

    @staticmethod
    def post():
        """Logic for POST events. Sets the seed of the simulator"""

        req_args = utils.parse_args(_PARSER)
        seed: int = req_args["value"]

        if not is_valid_seed(seed):
            return responses.bad_request_resp(
                "Invalid seed specified. Must be a positive integer less than 2^32"
            )

        err = utils.sim_proxy().simulation.set_seed(seed)
        return responses.checked_resp(err)
