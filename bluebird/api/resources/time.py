"""
Provides logic for the TIME (get simulator time) API endpoint
"""

import logging

from flask_restful import Resource

from bluebird.api.resources.utils.responses import internal_err_resp, ok_resp


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

        time = sim_client().get_sim_time()

        if not time:
            return internal_err_resp("No time data received")

        # TODO Move this to simclient and just return the UTC from get_sim_time
        date_time = " ".join(time[0].split()[3:])
        data = {"sim_utc": date_time}
        return ok_resp(data)
