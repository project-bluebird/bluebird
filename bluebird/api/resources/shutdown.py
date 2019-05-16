"""
Provides logic for the shutdown endpoint
"""

# TODO Optionally shutdown any attached simulators

from flask import jsonify, request
from flask_restful import Resource


class Shutdown(Resource):
	"""
	Contains logic for the shutdown endpoint
	"""

	@staticmethod
	def post():
		"""
		Shuts down the BlueBird server
		:return: :class:`~flask.Response`
		"""

		try:
			request.environ.get('werkzeug.server.shutdown')()
		except Exception as exc:
			resp = jsonify(f'Could not shutdown: {exc}')
			resp.status_code = 500
			return resp

		resp = jsonify('Shutting down')
		resp.status_code = 200
		return resp
