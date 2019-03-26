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

		reset = bb_client.CLIENT_SIM.reset_sim()

		resp = jsonify('Simulation {} reset'.format('' if reset else 'not '))
		resp.status_code = 200 if reset else 500

		return resp
