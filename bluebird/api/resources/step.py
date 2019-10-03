"""
Provides logic for the STEP API endpoint
"""

from flask_restful import Resource

import bluebird.settings as bb_settings
from bluebird.api.resources.utils import (
    ac_data,
    sim_client,
    bad_request_resp,
    checked_resp,
)


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

        if bb_settings.SIM_MODE != bb_settings.SimMode.Agent:
            return bad_request_resp("Must be in agent mode to use step")

        err = sim_client().step_sim()

        if not err:
            ac_data().log()

        return checked_resp(err)
