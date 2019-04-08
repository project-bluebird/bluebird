"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client

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
		filename = parsed['filename']

		if filename is None or not filename.lower().endswith('.scn'):
			resp = jsonify(f'Invalid filename {filename}')
			resp.status_code = 400
			return resp

		multiplier = parsed['multiplier']
		speed = multiplier if multiplier else 1.0

		if speed <= 0.0:
			resp = jsonify(f'Invalid speed {speed}')
			resp.status_code = 400
			return resp

		err = bb_client.CLIENT_SIM.load_scenario(filename, speed=speed)

		if not err:
			resp = jsonify('Scenario file {} loaded'.format(filename))
			resp.status_code = 200
		else:
			resp = jsonify('Error: Could not load scenario {}. Error was: {}'.format(filename, err))
			resp.status_code = 500

		return resp
