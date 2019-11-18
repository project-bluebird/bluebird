"""
Provides logic for the OP (operate) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils.responses import checked_resp, bad_request_resp
from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode


class Op(Resource):
    """
    OP (operate) command

    Start's the simulation if in sandbox (free-run) mode
    """

    @staticmethod
    def post():
        """
        POST the OP (operate/resume) command and process the response.
        :return:
        """

        if Settings.SIM_MODE != SimMode.Sandbox:
            return bad_request_resp(
                f"Can't resume sim from mode {Settings.SIM_MODE.name}"
            )

        err = sim_proxy().simulation.resume()

        return checked_resp(err)
