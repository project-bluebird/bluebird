"""
Provides logic for the OP (operate) API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode


class Op(Resource):
    """OP (operate) command. Start's the simulation if in sandbox mode"""

    @staticmethod
    def post():
        """Logic for post events"""

        if Settings.SIM_MODE != SimMode.Sandbox:
            return responses.bad_request_resp(
                f"Can't resume sim from mode {Settings.SIM_MODE.name}"
            )

        err = utils.sim_proxy().simulation.resume()

        return responses.checked_resp(err)
