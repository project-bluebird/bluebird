"""
Provides logic for the SPD (horizontal speed) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

REQ_ARGS = ['spd']
PARSER = generate_arg_parser(REQ_ARGS)


class Spd(Resource):
	"""
	Contains logic for the SPD endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
		to alter its horizontal speed.
		:return: :class:`~flask.Response`
		"""

		return process_ac_cmd('SPD', PARSER, REQ_ARGS)
