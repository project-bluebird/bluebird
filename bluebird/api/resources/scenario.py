"""
Provides logic for the scenario (upload scenario) API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client

_LOGGER = logging.getLogger('bluebird')

PARSER = reqparse.RequestParser()
# TODO assert ends with .scn?
PARSER.add_argument('scn_name', type=str, location='json', required=True)
PARSER.add_argument('content', type=str, location='json', required=True, action='append')


def validate_scenario(scenario):
	"""

	:param scenario:
	:return:
	"""

	return None


# TODO option - reset and load scenario after uploading
class Scenario(Resource):
	"""
	Contains logic for the scenario endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events.
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		scn_name = parsed['scn_name']
		content = parsed['content']

		err = validate_scenario(content)

		if err:
			resp = jsonify(f'Invalid content: {err}')
			resp.status_code = 404
			return resp

		err = bb_client.CLIENT_SIM.upload_new_scenario(scn_name, content)

		if err:
			resp = jsonify(f'Error uploading scenario: {err}')
			resp.status_code = 500
		else:
			resp = jsonify(f'Scenario {scn_name} uploaded')
			resp.status_code = 201

		return resp
