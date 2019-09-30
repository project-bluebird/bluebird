"""
Provides logic for the HOLD (simulation pause) API endpoint
"""


from flask_restful import Resource

from bluebird.api.resources.utils import sim_client, checked_resp


class Hold(Resource):
    """
    HOLD (simulation pause) command
    """

    @staticmethod
    def post():
        """
        Pauses the simulation
        :return:
        """

        err = sim_client().pause_sim()

        return checked_resp(err)
