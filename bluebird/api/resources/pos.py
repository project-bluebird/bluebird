"""
Provides logic for the POST (position) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.cache import AC_DATA


class Pos(Resource):
	"""
	BlueSky POS (position) command
	"""

	@staticmethod
	def get(acid):
		"""
		Logic for GET events. If the request contains an identifier to an existing aircraft,
		then information about that aircraft is returned. Otherwise returns a 404.
		:return: :class:`~flask.Response`
		"""

		data = AC_DATA.get(acid)

		if data is None:
			return 'No data', 404

		resp = jsonify(data)
		resp.status_code = 200
		return resp
