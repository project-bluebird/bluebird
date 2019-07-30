"""
Provides logic for the SEED (set seed) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client

PARSER = reqparse.RequestParser()
PARSER.add_argument('value', type=int, location='json', required=True)


class Seed(Resource):
	"""
	BlueSky SEED (set seed) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Sets the seed of the simulator
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		seed = parsed['value']

		if not seed or seed < 0 or int(seed) >> 32:
			resp = jsonify(f'Invalid seed specified. Must be a positive integer less than 2^32')
			resp.status_code = 400
			return resp

		# TODO Wrap this into a method
		err = bb_client.CLIENT_SIM.send_stack_cmd(f'SEED {seed}')

		if not err:
			resp = jsonify('Seed set')
			resp.status_code = 200
		else:
			resp = jsonify(f'Error: Could not set seed. Error was: {err}')
			resp.status_code = 500

		bb_client.CLIENT_SIM.seed = seed  # Store the seed so we can use it in the episode logs
		return resp
