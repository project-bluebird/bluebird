"""
Provides logic for the 'eplog' (episode log file) API endpoint
"""

import os

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.client as bb_client
import bluebird.logging as bb_logging

PARSER = reqparse.RequestParser()
PARSER.add_argument('close_ep', type=bool, location='args', required=False)


class EpLog(Resource):
	"""
	Contains logic for the eplog endpoint
	"""

	@staticmethod
	def get():
		"""
		Logic for GET events.
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args(strict=True)
		close_ep = not parsed['close_ep'] is None

		ep_file_path = bb_logging.EP_FILE

		if not ep_file_path:
			resp = jsonify('Error: No episode being recorded')
			resp.status_code = 404
			return resp

		if close_ep:
			err = bb_client.CLIENT_SIM.reset_sim()
			if err:
				resp = jsonify(f'Could not reset simulation: {err}')
				resp.status_code = 500
				return resp

		full_ep_file = os.path.join(os.getcwd(), ep_file_path)
		lines = tuple(line.rstrip('\n') for line in open(full_ep_file))

		resp = jsonify({'cur_ep_id': bb_logging.EP_ID, 'cur_ep_file': full_ep_file, 'lines': lines})
		resp.status_code = 200
		return resp
