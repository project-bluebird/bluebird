"""
Provides logic for the OP (operate) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.client import CLIENT_SIM


class Op(Resource):
	"""
	BlueSky OP (operate) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events.
		:return: :class:`~flask.Response`
		"""

		CLIENT_SIM.send_stack_cmd('OP')

		# TODO Handle response from simulation
		resp = jsonify('Ok?')
		resp.status_code = 418
		return resp
