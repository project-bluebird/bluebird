"""
Provides logic for the STEP API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.utils.properties import SimMode
from bluebird.settings import Settings


# TODO SimClient's should assert (internally) that the simulator time is advanced
class Step(Resource):
    """
    Contains logic for the step endpoint
    """

    @staticmethod
    def post():
        """
        Logic for POST events
        :return:
        """

        if Settings.SIM_MODE != SimMode.Agent:
            return responses.bad_request_resp("Must be in agent mode to use step")

        err = sim_proxy().simulation.step()

        return responses.checked_resp(err)
