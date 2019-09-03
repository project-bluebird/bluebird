
from flask import jsonify
from flask_restful import Resource

import bluebird.settings as bb_settings

class Sectors(Resource):

	@staticmethod
	def get():
		"""
		Gets all the defined sectors (if any)
		"""

		resp = jsonify({'sectors': bb_settings.SECTORS})
		resp.status_code = 200
		return resp
