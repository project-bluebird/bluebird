"""
Provides logic for the IC (initial condition) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.client import CLIENT_SIM

PARSER = reqparse.RequestParser()
PARSER.add_argument('filename', type=str, location='json', required=False)


class Ic(Resource):
	"""
	BlueSky IC (initial condition) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains a valid scenario filename, then that is
		loaded. Otherwise the currently running scenario is reset.
		:return: :class:`~flask.Response`
		"""

		filename = PARSER.parse_args()['filename']
		reset = CLIENT_SIM.reset_sim(filename)

		resp = jsonify('Simulation {}reset'.format('' if reset else 'not '))
		resp.status_code = 200 if reset else 500

		return resp
