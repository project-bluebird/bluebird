"""
Provides logic for the IC (initial condition) API endpoint
"""

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
		args = PARSER.parse_args()

		if args['filename'] is not None:
			cmd = args['filename']
		else:
			cmd = 'IC'

		CLIENT_SIM.send_stackcmd('IC ' + cmd)

		# TODO Get return status. Can hook this up to a 'SIMRESET' signal?
		return 'Ok?', 418
