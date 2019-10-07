"""
Provides logic for the RESET API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils.responses import checked_resp
from bluebird.api.resources.utils.utils import sim_proxy


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

        err = sim_proxy().reset_sim()

        return checked_resp(err)
