"""
Provides logic for the TIME (get simulator time) API endpoint
"""

import logging

from flask_restful import Resource

from bluebird.api.resources.utils.responses import internal_err_resp, ok_resp
from bluebird.api.resources.utils.utils import sim_proxy


_LOGGER = logging.getLogger(__name__)


class Time(Resource):
    """
    TIME (get simulator time) command
    """

    @staticmethod
    def get():
        """
        GET the current simulator time
        :return:
        """

        sim_utc = sim_proxy().sim_properties.sim_utc

        if not sim_utc:
            return internal_err_resp("Could not get sim time")

        data = {"sim_utc": sim_utc}
        return ok_resp(data)
