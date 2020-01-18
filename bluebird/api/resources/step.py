"""
Provides logic for the STEP API endpoint
"""
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode


# TODO SimClient's should assert (internally) that the simulator time is advanced
class Step(Resource):
    """Contains logic for the step endpoint"""

    @staticmethod
    def post():
        """Logic for POST events"""

        if Settings.SIM_MODE != SimMode.Agent:
            return responses.bad_request_resp("Must be in agent mode to use step")

        err = utils.sim_proxy().simulation.step()

        return responses.checked_resp(err)
