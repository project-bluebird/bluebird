"""
Provides logic for the CRE (create aircraft) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

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

		return process_ac_cmd('CRE', PARSER, REQ_ARGS, [], assert_exists=False)
