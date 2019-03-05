"""
Provides logic for the RESET API endpoint
"""

from flask import jsonify
from flask_restful import Resource

import bluebird.client as bb_client


class Reset(Resource):
	"""
	BlueSky RESET command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Resets and clears the simulation
		:return: :class:`~flask.Response`
		"""

		err = bb_client.CLIENT_SIM.reset_sim()

		if not err:
			resp = jsonify('Simulation reset')
			resp.status_code = 200
		else:
			resp = jsonify('Simulation now reset: '.format(err))
			resp.status_code = 500

		return resp
