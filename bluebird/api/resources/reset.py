"""
Provides logic for the RESET API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import sim_client, checked_resp


class Reset(Resource):
    """
    RESET command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. Resets and clears the simulation
        :return:
        """

        err = sim_client().reset_sim()

        return checked_resp(err)
