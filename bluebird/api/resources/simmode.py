"""
Provides logic for the SIM MODE API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.settings as settings

PARSER = reqparse.RequestParser()
PARSER.add_argument('mode', type=str, location='json', required=True)


class SimMode(Resource):
	"""
	Logic for the SimMode endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Changes the simulation mode
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		new_mode = parsed['mode']

		if not new_mode in settings.SIM_MODES:
			available = ','.join(settings.SIM_MODES)
			resp = jsonify(f'Mode \'{new_mode}\' not supported. Must be one of {available}')
			resp.status_code = 400
			return resp

		settings.SIM_MODE = new_mode

		resp = jsonify(f'Mode set to {settings.SIM_MODE}')
		resp.status_code = 200
		return resp
