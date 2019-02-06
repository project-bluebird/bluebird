"""
Provides logic for the POST (position) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.api.resources.utils import check_acid, generate_arg_parser
from bluebird.cache import AC_DATA

REQ_ARGS = []
PARSER = generate_arg_parser(REQ_ARGS)


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

		resp = check_acid(acid)
		if resp is not None:
			return resp

		resp = jsonify(AC_DATA.get(acid))
		resp.status_code = 200
		return resp
