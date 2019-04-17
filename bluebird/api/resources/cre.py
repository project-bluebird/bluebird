"""
Provides logic for the CRE (create aircraft) API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd
from bluebird.cache import AC_DATA

REQ_ARGS = ['type', 'lat', 'lon', 'hdg', 'alt', 'spd']
PARSER = generate_arg_parser(REQ_ARGS)


class Cre(Resource):
	"""
	BlueSky CRE (create aircraft) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains valid aircraft information, then a request is
		sent to the simulator to create it.
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args(strict=True)
		acid = parsed['acid']

		if AC_DATA.contains(acid):
			resp = jsonify('Aircraft {} already exists'.format(acid))
			resp.status_code = 400
			return resp

		return process_ac_cmd('CRE', PARSER, REQ_ARGS, [], assert_exists=False, success_code=201)
