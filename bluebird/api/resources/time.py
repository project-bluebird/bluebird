"""
Provides logic for the TIME (get simulator time) API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource

from bluebird.api.resources.utils import bb_app

_LOGGER = logging.getLogger("bluebird")


class Time(Resource):
    """
    BlueSky TIME (get simulated time) command
    """

    @staticmethod
    def get():
        """
        GET the current simulated time.
        :return: :class:`~flask.Response`
        """

        cmd_str = "TIME"

        _LOGGER.debug(f"Sending stack command: {cmd_str}")
        reply = bb_app().sim_client.send_stack_cmd(cmd_str, response_expected=True)

        if not reply:
            resp = jsonify("Error: No time data received from BlueSky")
            resp.status_code = 500
            return resp

        date_time = " ".join(reply[0].split()[3:])
        resp = jsonify({"sim_utc": date_time})
        resp.status_code = 200
        return resp
