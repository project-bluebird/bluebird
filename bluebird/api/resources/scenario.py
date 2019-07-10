"""
Provides logic for the scenario (create scenario) API endpoint
"""

import logging

import re
import time
from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client
from bluebird.cache import AC_DATA
from bluebird.logging import store_local_scn

_LOGGER = logging.getLogger('bluebird')

PARSER = reqparse.RequestParser()
PARSER.add_argument('scn_name', type=str, location='json', required=True)
PARSER.add_argument('content', type=str, location='json', required=True, action='append')
PARSER.add_argument('start_new', type=bool, location='json', required=False)
PARSER.add_argument('start_dtmult', type=float, location='json', required=False)

_SCN_RE = re.compile(r'\d{2}:\d{2}:\d{2}(\.\d{1,3})?\s?>\s?.*')


def _validate_scenario(scn_lines):
	"""
	Checks that each line in the given list matches the requirements
	:param scn_lines:
	:return:
	"""

	for line in scn_lines:
		if not _SCN_RE.match(line):
			return f'Line \'{line}\' does not match the required format'

	return None


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

		scn_name = scn_base = parsed['scn_name']

		if not scn_name.endswith('.scn'):
			scn_name += '.scn'

		if scn_name.startswith('scenario'):
			scn_name = scn_name[len('scenario') + 1:]

		content = parsed['content']
		err = _validate_scenario(content)

		if err:
			resp = jsonify(f'Invalid scenario content: {err}')
			resp.status_code = 400
			return resp

		store_local_scn(scn_name, content)

		err = bb_client.CLIENT_SIM.upload_new_scenario(scn_name, content)

		if err:
			resp = jsonify(f'Error uploading scenario: {err}')
			resp.status_code = 500

		elif parsed['start_new']:

			dtmult = parsed['start_dtmult'] if parsed['start_dtmult'] else 1.0
			err = bb_client.CLIENT_SIM.load_scenario(scn_name, speed=dtmult)

			if err:
				resp = jsonify(f'Could not start scenario after upload: {err}')
				resp.status_code = 500
			else:
				resp = jsonify(f'Scenario {scn_base} uploaded and started')
				resp.status_code = 200

		else:
			resp = jsonify(f'Scenario {scn_base} uploaded')
			resp.status_code = 201

		# Wait for the data store to be populated
		while not len(AC_DATA.store):
			time.sleep(0.1)

		return resp
