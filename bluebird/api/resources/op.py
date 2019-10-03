"""
Provides logic for the OP (operate) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import sim_client, checked_resp


class Op(Resource):
    """
    OP (operate) command
    """

    @staticmethod
    def post():
        """
        POST the OP (operate/resume) command and process the response.
        :return:
        """

        err = sim_client().resume_sim()

        return checked_resp(err)
