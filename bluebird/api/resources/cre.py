"""
Provides logic for the CRE (create aircraft) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.client import CLIENT_SIM

# TODO Tidy this (can we define as a dict?)
PARSER = reqparse.RequestParser()
PARSER.add_argument('acid', type=str, location='json', required=True)
PARSER.add_argument('type', type=str, location='json', required=True)
PARSER.add_argument('lat', type=str, location='json', required=True)
PARSER.add_argument('lon', type=str, location='json', required=True)
PARSER.add_argument('hdg', type=str, location='json', required=True)
PARSER.add_argument('alt', type=str, location='json', required=True)
PARSER.add_argument('spd', type=str, location='json', required=True)


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

		args = PARSER.parse_args()
		cmd = 'CRE {acid} {type} {lat} {lon} {hdg} {alt} {spd}'.format(**args)

		CLIENT_SIM.send_stackcmd(cmd)

		# TODO Get return status. Can check for the created aircraft? What does BlueSky
		# return on an error?
		return 'Ok?', 418
