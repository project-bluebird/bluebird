"""
Provides logic for the RESET API endpoint
"""

from flask import jsonify
from flask_restful import Resource

from bluebird.api.resources.utils import bb_app


class Reset(Resource):
    """
	BlueSky RESET command
	"""

    @staticmethod
    def post():
        """
		Logic for POST events. Resets and clears the simulation
		:return: :class:`~flask.Response`
		"""

        err = bb_app().sim_client.reset_sim()

        if not err:
            resp = jsonify("Simulation reset")
            resp.status_code = 200
        else:
            resp = jsonify(f"Simulation not reset: {err}")
            resp.status_code = 500

        return resp
