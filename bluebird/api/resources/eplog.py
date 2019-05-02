"""
Provides logic for the 'eplog' (episode log file) API endpoint
"""

import os

from flask import jsonify
from flask_restful import Resource

import bluebird.logging as bb_logging


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

		ep_file_path = bb_logging.EP_FILE

		if not ep_file_path:
			resp = jsonify('Error: No episode being recorded')
			resp.status_code = 404
			return resp

		full_ep_file = os.path.join(os.getcwd(), ep_file_path)
		lines = tuple(open(full_ep_file, 'r'))

		resp = jsonify({'cur_ep_id': bb_logging.EP_ID, 'cur_ep_file': full_ep_file, 'lines': lines})
		resp.status_code = 200
		return resp
