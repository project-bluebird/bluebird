"""
Provides logic for the HOLD (simulation pause) API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.utils as utils
import bluebird.api.resources.utils.responses as responses
from bluebird.utils.properties import SimMode
from bluebird.settings import Settings


class Hold(Resource):
    """HOLD (simulation pause) command"""

    @staticmethod
    def post():
        """Pauses the simulation"""

        if Settings.SIM_MODE == SimMode.Agent:
            return responses.bad_request_resp("Can't pause while in agent mode")

        err = utils.sim_proxy().simulation.pause()

        return responses.checked_resp(err)
