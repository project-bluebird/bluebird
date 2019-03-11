"""
Provides logic for the OP (operate) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.api.resources.utils import process_stack_cmd

class Op(Resource):
	"""
	BlueSky OP (operate) command
	"""

	@staticmethod
	def post():
		"""
		POST the OP (operate/resume) command and process the response.
		:return: :class:`~flask.Response`
		"""

		return process_stack_cmd('OP')
