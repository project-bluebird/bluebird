"""
Provides logic for the SIM MODE API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.settings as settings
from bluebird.api.resources.utils import bb_app

_LOGGER = logging.getLogger('bluebird')
PARSER = reqparse.RequestParser()
PARSER.add_argument('mode', type=str, location='json', required=True)


class SimMode(Resource):
	"""
	Logic for the SimMode endpoint
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Changes the simulation mode
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args()
		new_mode = parsed['mode']

		if not new_mode in settings.SIM_MODES:
			available = ', '.join(settings.SIM_MODES)
			resp = jsonify(f'Mode \'{new_mode}\' not supported. Must be one of: {available}')
			resp.status_code = 400
			return resp

		_LOGGER.debug(f'Setting mode to {new_mode}')

		settings.SIM_MODE = new_mode

		if new_mode == 'agent':

			bb_app().ac_data.set_log_rate(0)

			err = bb_app().sim_client.send_stack_cmd('HOLD')
			if err:
				resp = jsonify(f'Could not pause sim when changing mode: {err}')
				resp.status_code = 500
				return resp

		elif new_mode == 'sandbox':

			bb_app().ac_data.resume_log()

			err = bb_app().sim_client.send_stack_cmd('OP')
			if err:
				resp = jsonify(f'Could not resume sim when changing mode: {err}')
				resp.status_code = 500
				return resp

		else:
			raise ValueError(f'Unsupported mode {new_mode}')

		resp = jsonify(f'Mode set to {settings.SIM_MODE}')
		resp.status_code = 200
		return resp
