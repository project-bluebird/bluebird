"""
Provides logic for the HOLD (simulation pause) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.client import CLIENT_SIM


class Hold(Resource):
	"""
	BlueSky HOLD (simulation pause) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events.
		:return: :class:`~flask.Response`
		"""

		CLIENT_SIM.send_stack_cmd('HOLD')

		# TODO Handle response from simulation
		resp = jsonify('Ok?')
		resp.status_code = 418
		return resp
