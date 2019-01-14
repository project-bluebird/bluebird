"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.cache import AC_DATA
from bluebird.client import CLIENT_SIM
from bluebird.utils.strings import is_acid

PARSER = reqparse.RequestParser()
PARSER.add_argument('acid', type=str, location='json', required=True)
PARSER.add_argument('alt', type=str, location='json', required=True)
PARSER.add_argument('vspd', type=str, location='json', required=False)


class Alt(Resource):
	"""
	Contains logic for the ALT endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
		to alter its altitude.
		:return: :class:`~flask.Response`
		"""

		args = PARSER.parse_args()

		acid = args['acid']

		if not is_acid(acid):
			resp = jsonify('Invalid ACID \'{}\''.format(acid))
			resp.status_code = 400
			return resp

		if AC_DATA.get(acid) is None:
			resp = jsonify('AC {} not found'.format(acid))
			resp.status_code = 404
			return resp

		cmd = 'ALT {acid} {alt} '.format(**args)

		if args['vspd'] is not None:
			cmd += args['vspd']

		CLIENT_SIM.send_stackcmd(cmd)

		# TODO Handle response from simulation
		resp = jsonify('Ok?')
		resp.status_code = 418
		return resp
