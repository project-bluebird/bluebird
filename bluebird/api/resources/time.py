"""
Provides logic for the TIME (get or set simulator time) API endpoint
"""

# TODO The date can also be specified, although this is not referenced in the BlueSky docs

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client

_LOGGER = logging.getLogger('bluebird')

PARSER = reqparse.RequestParser()
PARSER.add_argument('time', type=str, location='json', required=False)


class Time(Resource):
	"""
	BlueSky TIME (get/set simulated time) command
	"""

	@staticmethod
	def post():
		"""
		POST the TIME command and process the response.
		:return: :class:`~flask.Response`
		"""

		time = PARSER.parse_args()['time']
		cmd_str = 'TIME ' + (time if time else '')

		_LOGGER.info(f'Sending stack command: {cmd_str}')
		reply = bluebird.client.CLIENT_SIM.send_stack_cmd(cmd_str, response_expected=True)

		if not reply:
			resp = jsonify('Error: No route data received from BlueSky')
			resp.status_code = 500
			return resp

		resp = jsonify(reply)
		resp.status_code = 200
		return resp
