"""
Provides logic for the POST (position) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import check_acid
from bluebird.cache import AC_DATA

PARSER = reqparse.RequestParser()
PARSER.add_argument('acid', type=str, location='args', required=True)


class Pos(Resource):
	"""
	BlueSky POS (position) command
	"""

	@staticmethod
	def get():
		"""
		Logic for GET events. If the request contains an identifier to an existing aircraft,
		then information about that aircraft is returned. Otherwise returns a 404.
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		acid = parsed['acid']

		if acid == '':
			resp = jsonify('No ACID provided')
			resp.status_code = 400
			return resp

		if acid.upper() == 'ALL':
			if not AC_DATA.store:
				resp = jsonify('No aircraft in the simulation')
				resp.status_code = 400
				return resp
		else:
			resp = check_acid(acid)
			if resp is not None:
				return resp

		resp = jsonify(AC_DATA.get(acid))
		resp.status_code = 200
		return resp
