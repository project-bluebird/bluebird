"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client

PARSER = reqparse.RequestParser()
PARSER.add_argument('filename', type=str, location='json', required=True)


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

		filename = PARSER.parse_args()['filename']

		if filename is None or not filename.lower().endswith('.scn'):
			resp = jsonify('Invalid filename ' + filename)
			resp.status_code = 400
			return resp

		loaded = bb_client.CLIENT_SIM.load_scenario(filename)

		if loaded:
			resp = jsonify('Scenario file {} loaded'.format(filename))
			resp.status_code = 200
		else:
			resp = jsonify('Error: Could not load scenario {}'.format(filename))
			resp.status_code = 500

		return resp
