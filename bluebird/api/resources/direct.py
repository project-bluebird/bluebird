"""
Provides logic for the DIRECT API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import generate_arg_parser, process_ac_cmd

REQ_ARGS = ['waypoint']
PARSER = generate_arg_parser(REQ_ARGS)


class Direct(Resource):
	"""
	Contains logic for the DIRECT endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
		to move directly to the specified waypoint. The specified waypoint must exist on the
		aircraft's route.
		:return: :class:`~flask.Response`
		"""

		return process_ac_cmd('DIRECT', PARSER, REQ_ARGS)
