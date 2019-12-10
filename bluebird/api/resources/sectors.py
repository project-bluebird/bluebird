"""
Provides logic for the sectors API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


class Sectors(Resource):
    """
    Contains logic for the SECTORS endpoint
    """

    @staticmethod
    def get():
        """Returns all the sectors defined in the current simulation"""

        sectors = utils.sim_proxy().sectors

        return responses.ok_resp({"sectors": sectors})
