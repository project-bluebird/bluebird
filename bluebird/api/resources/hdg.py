"""
Provides logic for the HDG (heading) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

REQ_ARGS = ["hdg"]
PARSER = generate_arg_parser(REQ_ARGS)


class Hdg(Resource):
    """
    Contains logic for the HDG endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
        to alter its heading.
        :return: :class:`~flask.Response`
        """

        return process_ac_cmd("HDG", PARSER, REQ_ARGS)
