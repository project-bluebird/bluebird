"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

REQ_ARGS = ['alt']
OPT_ARGS = ['vspd']
PARSER = generate_arg_parser(REQ_ARGS, OPT_ARGS)


class Alt(Resource):
	"""
	BlueSky ALT (altitude) command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
		to alter its altitude.
		:return: :class:`~flask.Response`
		"""

		return process_ac_cmd('ALT', PARSER, REQ_ARGS, OPT_ARGS)
