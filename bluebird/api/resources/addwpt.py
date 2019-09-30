"""
Provides logic for the ADDWPT (add waypoint) API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import check_acid, process_stack_cmd

_LOGGER = logging.getLogger("bluebird")

PARSER = reqparse.RequestParser()
PARSER.add_argument("acid", type=str, location="json", required=True)
PARSER.add_argument("wpname", type=str, location="json", required=False)
PARSER.add_argument("lat", type=float, location="json", required=False)
PARSER.add_argument("lon", type=float, location="json", required=False)
PARSER.add_argument("alt", type=str, location="json", required=False)
PARSER.add_argument("spd", type=float, location="json", required=False)


class AddWpt(Resource):
    """
	BlueSky ADDWPT (add waypoint) command
	"""

    @staticmethod
    def post():
        """
		Logic for POST events. If the request is valid, then the specified waypoint is added to the
		aircraft's route
		:return: :class:`~flask.Response`
		"""

        parsed = PARSER.parse_args()
        acid = parsed["acid"]

        resp = check_acid(acid)
        if resp is not None:
            return resp

        cmd_str = f"ADDWPT {acid} "

        # TODO Tidy this

        if parsed["wpname"]:
            cmd_str += parsed["wpname"]
        elif parsed["lat"] and parsed["lon"]:
            cmd_str += f'{parsed["lat"]} {parsed["lon"]}'
        else:
            resp = jsonify(
                "Must provide either a waypoint, or a latitude and longitude"
            )
            resp.status_code = 400
            return resp

        cmd_str += f' {parsed["alt"]}' if parsed["alt"] else ""
        cmd_str += f' {parsed["spd"]}' if parsed["spd"] else ""

        return process_stack_cmd(cmd_str)
