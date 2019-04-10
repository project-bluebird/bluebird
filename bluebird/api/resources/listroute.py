"""
Provides logic for the LISTROUTE (list route) API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client
from bluebird.api.resources.utils import check_acid

PARSER = reqparse.RequestParser()
PARSER.add_argument('acid', type=str, location='args', required=True)

_LOGGER = logging.getLogger('bluebird')


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
		acid = parsed['acid']

		resp = check_acid(acid)
		if resp is not None:
			return resp

		cmd_str = f'LISTRTE {acid}'
		_LOGGER.debug(f'Sending stack command: {cmd_str}')
		reply = bluebird.client.CLIENT_SIM.send_stack_cmd(cmd_str, response_expected=True)

		if not reply:
			resp = jsonify('Error: No route data received from BlueSky')
			resp.status_code = 500
			return resp

		if not isinstance(reply, list):
			resp = jsonify(f'Simulation returned: {reply}')
			resp.status_code = 500
			return resp

		resp = jsonify({'route': reply})
		resp.status_code = 200
		return resp
