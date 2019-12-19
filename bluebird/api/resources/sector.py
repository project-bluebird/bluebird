"""
Provides logic for the sector API endpoint
"""

from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


class Sector(Resource):
    """
    Contains logic for the SECTOR endpoint
    """

    @staticmethod
    def get():
        """Returns the sector defined in the current simulation"""

        if not hasattr(utils.sim_proxy(), "sector"):
            return responses.internal_err_resp("No sector has been set")

        sector = utils.sim_proxy().sector

        return responses.ok_resp({"sector": sector})
