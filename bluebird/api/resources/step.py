"""
Provides logic for the STEP API endpoint
"""

from flask import jsonify
from flask_restful import Resource

import bluebird.settings as settings
from bluebird.api.resources.utils import bb_app


class Step(Resource):
    """
    Contains logic for the step endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events.
        :return: :class:`~flask.Response`
        """

        if settings.SIM_MODE != "agent":
            resp = jsonify("Must be in agent mode to use step")
            resp.status_code = 400
            return resp

        err = bb_app().sim_client.step()

        if not err:
            resp = jsonify("Simulation stepped")
            resp.status_code = 200
        else:
            resp = jsonify(f"Could not step simulations: {err}")
            resp.status_code = 500

        bb_app().ac_data.log()

        return resp
