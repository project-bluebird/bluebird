"""
Provides logic for the Load Log API endpoint
"""

import logging
import os

import uuid
from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.cache as bb_cache
import bluebird.client as bb_client
import bluebird.settings
from bluebird.api.resources.utils import parse_lines, validate_scenario, wait_for_data, \
	wait_for_pause
from bluebird.logging import store_local_scn
from bluebird.utils.timeutils import timeit

_LOGGER = logging.getLogger(__name__)

PARSER = reqparse.RequestParser()
PARSER.add_argument('filename', type=str, location='json', required=False)
PARSER.add_argument('lines', type=str, location='json', required=False, action='append')
PARSER.add_argument('time', type=int, location='json', required=True)


class LoadLog(Resource):
	"""
	Contains logic for the Load Log endpoint
	"""

	@staticmethod
	@timeit('LoadLog')
	def post():
		"""
		Logic for POST events. Returns the simulator to a previous state given a logfile
		:return: :class:`~flask.Response`
		"""

		if bluebird.settings.SIM_MODE != 'agent':
			resp = jsonify('Can only be used in agent mode')
			resp.status_code = 400
			return resp

		parsed = PARSER.parse_args()
		if bool(parsed['filename']) == bool(parsed['lines']):
			resp = jsonify('Either filename or lines must be specified')
			resp.status_code = 400
			return resp

		target_time = parsed['time']
		if target_time < 0:
			resp = jsonify('Target time must be positive')
			resp.status_code = 400
			return resp

		prev_dt = bb_client.CLIENT_SIM.step_dt

		_LOGGER.debug('Starting log reload')

		# Reset now so the current episode log is closed
		err = bb_client.CLIENT_SIM.reset_sim()

		if err:
			resp = jsonify(f'Simulation not reset: {err}')
			resp.status_code = 500

		if parsed['filename']:
			if not os.path.exists(parsed['filename']):
				resp = jsonify(f'Could not find episode file {parsed["filename"]}')
				resp.status_code = 400
				return resp
			lines = tuple(open(parsed['filename'], 'r'))
		else:
			lines = parsed['lines']

		_LOGGER.debug('Parsing log content')
		parsed_scn = parse_lines(lines, target_time)

		if isinstance(parsed_scn, str):
			resp = jsonify(f'Could not parse episode content: {parsed_scn}')
			resp.status_code = 400
			return resp

		err = validate_scenario(parsed_scn['lines'])

		if err:
			resp = jsonify('Could not create a valid scenario from the given log')
			resp.status_code = 400
			return resp

		# All good - do the reload

		_LOGGER.debug('Setting the simulator seed')
		err = bb_client.CLIENT_SIM.send_stack_cmd(f'SEED {parsed_scn["seed"]}')

		if err:
			resp = jsonify(f'Could not set seed {err}')
			resp.status_code = 500

		bb_client.CLIENT_SIM.seed = parsed_scn["seed"]

		scn_name = f'reloads/{str(uuid.uuid4())[:8]}.scn'

		_LOGGER.debug('Uploading the new scenario')
		store_local_scn(scn_name, parsed_scn['lines'])
		err = bb_client.CLIENT_SIM.upload_new_scenario(scn_name, parsed_scn['lines'])

		if err:
			resp = jsonify(f'Error uploading scenario: {err}')
			resp.status_code = 500

		_LOGGER.debug('Starting the new scenario')
		err = bb_client.CLIENT_SIM.load_scenario(scn_name, start_paused=True)

		if err:
			resp = jsonify('Could not start scenario after upload')
			resp.status_code = 500
			return resp

		_LOGGER.debug('Waiting for simulation to be paused')
		wait_for_pause()

		diff = target_time - bb_cache.SIM_STATE.sim_t

		# Naive approach - set DTMULT to target, then STEP once...
		_LOGGER.debug(f'Time difference is {diff}. Stepping to {target_time}')
		err = bb_client.CLIENT_SIM.send_stack_cmd(f'DTMULT {diff}')

		if err:
			resp = jsonify(f'Could not change speed: {err}')
			resp.status_code = 500
			return resp

		_LOGGER.debug('Performing step')
		err = bb_client.CLIENT_SIM.step()

		if err:
			resp = jsonify(f'Could not step simulations: {err}')
			resp.status_code = 500
			return resp

		_LOGGER.debug('Waiting for AC_DATA to catch up')
		wait_for_data()
		bb_cache.AC_DATA.log()

		# Reset DTMULT to the previous value
		err = bb_client.CLIENT_SIM.send_stack_cmd(f'DTMULT {prev_dt}')

		if err:
			resp = jsonify(f'Episode reloaded, but could not reset DTMULT to previous value')
			resp.status_code = 500
			return resp

		# TODO Do we want to check before/after positions here and check if the differences are
		# acceptable?

		resp = jsonify('Simulation reloaded')
		resp.status_code = 200
		return resp
