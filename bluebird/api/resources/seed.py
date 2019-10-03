"""
Provides logic for the SEED (set seed) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import (
    sim_client,
    parse_args,
    checked_resp,
    bad_request_resp,
)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("value", type=int, location="json", required=True)


class Seed(Resource):
    """
    SEED (set seed) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. Sets the seed of the simulator
        :return:
        """

        req_args = parse_args(_PARSER)
        seed = req_args["value"]

        if seed < 0 or seed >> 32:
            return bad_request_resp(
                "Invalid seed specified. Must be a positive integer less than 2^32"
            )

        # TODO AbstractClient needs to have the 'seed' property
        err = sim_client().set_seed(seed)

        return checked_resp(err)
