"""
Provides logic for the OP (operate) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils.responses import checked_resp
from bluebird.api.resources.utils.utils import sim_proxy


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

        err = sim_proxy().start_or_resume_sim()

        return checked_resp(err)
