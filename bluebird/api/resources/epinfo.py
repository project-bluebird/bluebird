"""
Provides logic for the epinfo (episode info) API endpoint
"""

import os

from flask import jsonify
from flask_restful import Resource

import bluebird.logging as bb_logging


class EpInfo(Resource):
	"""
	Contains logic for the epinfo endpoint
	"""

	@staticmethod
	def get():
		"""
		Logic for GET events.
		:return: :class:`~flask.Response`
		"""

		full_log_dir = os.path.join(os.getcwd(), bb_logging.INST_LOG_DIR)
		full_ep_file = os.path.join(os.getcwd(), bb_logging.EP_FILE)

		resp = jsonify({'inst_id': bb_logging.INSTANCE_ID, 'cur_ep_id': bb_logging.EP_ID,
		                'cur_ep_file': full_ep_file, 'log_dir': full_log_dir})
		resp.status_code = 200

		return resp
