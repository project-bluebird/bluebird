"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client
import bluebird.settings as settings

PARSER = reqparse.RequestParser()
PARSER.add_argument('filename', type=str, location='json', required=True)
PARSER.add_argument('multiplier', type=float, location='json', required=False)


class Ic(Resource):
	"""
	BlueSky IC (initial condition) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Loads the scenario contained in the given file
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		filename = fn_base = parsed['filename']

		if not filename:
			resp = jsonify(f'No filename specified')
			resp.status_code = 400
			return resp

		if not filename.lower().endswith('.scn'):
			filename += '.scn'

		multiplier = parsed['multiplier']
		speed = multiplier if multiplier else 1.0

		if speed <= 0.0:
			resp = jsonify(f'Invalid speed {speed}')
			resp.status_code = 400
			return resp

		start_paused = settings.SIM_MODE == 'agent'
		err = bb_client.CLIENT_SIM.load_scenario(filename, speed=speed, start_paused=start_paused)

		if not err:
			resp = jsonify(f'Scenario {fn_base} loaded')
			resp.status_code = 200
		else:
			resp = jsonify(f'Error: Could not load scenario {fn_base}. Error was: {err}')
			resp.status_code = 500

		return resp
