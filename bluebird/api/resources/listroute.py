"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

import logging

import re
from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app, check_acid

PARSER = reqparse.RequestParser()
PARSER.add_argument("acid", type=str, location="args", required=True)

_LOGGER = logging.getLogger("bluebird")

_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


def parse_route_data(route_data):
    """
	Parse a list of strings containing route data into a keyed dictionary
	:param route_data:
	:return:
	"""

    parsed = []
    for line in map(lambda s: s.replace(" ", ""), route_data):
        match = _ROUTE_RE.match(line)
        if not match:
            return line
        req_alt = match.group(3) if not "-" in match.group(3) else None
        req_spd = int(match.group(4)) if not "-" in match.group(4) else None
        parsed.append(
            {
                "is_current": bool(match.group(1)),
                "wpt_name": match.group(2),
                "req_alt": req_alt,
                "req_spd": req_spd,
            }
        )
    return parsed


class ListRoute(Resource):
    """
	Contains logic for the LISTROUTE endpoint
	"""

    @staticmethod
    def get():
        """
		Logic for GET events. If the request contains an identifier to an existing aircraft,
		then information about its route (FMS flightplan) is returned.
		:return: :class:`~flask.Response`
		"""

        parsed = PARSER.parse_args()
        acid = parsed["acid"]

        resp = check_acid(acid)
        if resp is not None:
            return resp

        cmd_str = f"LISTRTE {acid}"
        _LOGGER.debug(f"Sending stack command: {cmd_str}")
        reply = bb_app().sim_client.send_stack_cmd(cmd_str, response_expected=True)

        if not reply:
            resp = jsonify("Error: No route data received from BlueSky")
            resp.status_code = 500
            return resp

        if not isinstance(reply, list):
            resp = jsonify(f"Simulation returned: {reply}")
            resp.status_code = 500
            return resp

        parsed_route = parse_route_data(reply)

        if not isinstance(parsed_route, list):
            resp = jsonify(f"Error: Could not parse route entry {parsed_route}")
            resp.status_code = 500
            return resp

        sim_t = bb_app().sim_state.sim_t
        resp = jsonify({"route": parsed_route, "acid": acid, "sim_t": sim_t})
        resp.status_code = 200
        return resp
