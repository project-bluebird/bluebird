"""
Provides logic for the DTMULT API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app

PARSER = reqparse.RequestParser()
PARSER.add_argument('multiplier', type=float, location='json', required=True)


class DtMult(Resource):
	"""
	BlueSky DTMULT command
	"""

	@staticmethod
	def post():
		"""
		Logic for POST events. Sets the speed multiplier for the simulation
		:return: :class:`~flask.Response`
		"""

		parsed = PARSER.parse_args(strict=True)
		mult = round(parsed['multiplier'], 2)

		if mult <= 0:
			resp = jsonify('Multiplier must be greater than 0')
			resp.status_code = 400
			return resp

		cmd = f'DTMULT {mult}'
		err = bb_app().sim_client.send_stack_cmd(cmd)

		if not err:
			bb_app().ac_data.set_log_rate(mult)
			resp = jsonify('Simulation speed changed')
			resp.status_code = 200
		else:
			resp = jsonify(f'Could not change speed: {err}')
			resp.status_code = 500

		bb_app().sim_client.step_dt = mult
		return resp
