"""
Provides logic for the VS (vertical speed) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

REQ_ARGS = []
OPT_ARGS = ["vspd"]
PARSER = generate_arg_parser(REQ_ARGS, OPT_ARGS)


class Vs(Resource):
    """
    Contains logic for the VS endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
        to alter its vertical speed.
        :return: :class:`~flask.Response`
        """

        return process_ac_cmd("VS", PARSER, REQ_ARGS, OPT_ARGS)
