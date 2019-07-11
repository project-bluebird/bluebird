"""
Provides logic for the Load Log API endpoint
"""

import os

import uuid
from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird.cache as bb_cache
import bluebird.client as bb_client
import bluebird.settings
from bluebird.api.resources.utils import parse_lines, validate_scenario, wait_for_data

PARSER = reqparse.RequestParser()
PARSER.add_argument('filename', type=str, location='json', required=False)
PARSER.add_argument('lines', type=str, location='json', required=False, action='append')
PARSER.add_argument('time', type=int, location='json', required=True)


class LoadLog(Resource):
	"""
	Contains logic for the Load Log endpoint
	"""

	@staticmethod
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

		if parsed['filename']:
			if not os.path.exists(parsed['filename']):
				resp = jsonify(f'Could not find episode file {parsed["filename"]}')
				resp.status_code = 400
				return resp
			lines = tuple(open(parsed['filename'], 'r'))
		else:
			lines = parsed['lines']

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

		err = bb_client.CLIENT_SIM.reset_sim()

		if err:
			resp = jsonify(f'Simulation not reset: {err}')
			resp.status_code = 500

		err = bb_client.CLIENT_SIM.send_stack_cmd(f'SEED {parsed_scn["seed"]}')

		if err:
			resp = jsonify(f'Could not set seed {err}')
			resp.status_code = 500

		bb_client.CLIENT_SIM.seed = parsed_scn["seed"]

		scn_name = f'reload-{str(uuid.uuid4())[:8]}'
		err = bb_client.CLIENT_SIM.upload_new_scenario(scn_name, parsed_scn['lines'])

		if err:
			resp = jsonify(f'Error uploading scenario: {err}')
			resp.status_code = 500

		err = bb_client.CLIENT_SIM.load_scenario(scn_name)

		if err:
			resp = jsonify('Could not start scenario after upload')
			resp.status_code = 500
			return resp

		# Naive approach - set DTMULT to target, then STEP once...
		err = bb_client.CLIENT_SIM.send_stack_cmd(f'DTMULT {target_time}')

		if err:
			resp = jsonify(f'Could not change speed: {err}')
			resp.status_code = 500
			return resp

		err = bb_client.CLIENT_SIM.step()

		if err:
			resp = jsonify(f'Could not step simulations: {err}')
			resp.status_code = 500
			return resp

		bb_cache.AC_DATA.log()
		wait_for_data()

		resp = jsonify('Simulation reloaded')
		resp.status_code = 200
		return resp
