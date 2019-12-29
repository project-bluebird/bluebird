"""
Provides logic for the RESET API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.responses as properties
import bluebird.api.resources.utils.utils as utils


class Reset(Resource):
    """RESET command"""

    @staticmethod
    def post():
        """Logic for POST events. Resets and clears the simulation"""

        err = utils.sim_proxy().simulation.reset()

        return properties.checked_resp(err)
