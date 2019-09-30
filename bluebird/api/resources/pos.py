"""
Provides logic for the POST (position) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app, check_acid

PARSER = reqparse.RequestParser()
PARSER.add_argument("acid", type=str, location="args", required=True)


class Pos(Resource):
    """
    BlueSky POS (position) command
    """

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing aircraft,
        then information about that aircraft is returned. Otherwise returns a 404.
        :return: :class:`~flask.Response`
        """

        parsed = PARSER.parse_args()
        acid = parsed["acid"]

        if acid.upper() == "ALL":
            if not bb_app().ac_data.store:
                resp = jsonify("No aircraft in the simulation")
                resp.status_code = 400
                return resp
        else:
            resp = check_acid(acid)
            if resp is not None:
                return resp

        resp = jsonify(bb_app().ac_data.get(acid))
        resp.status_code = 200
        return resp
