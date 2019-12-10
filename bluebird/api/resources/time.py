"""
Provides logic for the TIME (get simulator time) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils.responses import internal_err_resp, ok_resp
from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.utils.properties import SimProperties


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

        props = sim_proxy().simulation.properties
        if not isinstance(props, SimProperties):
            return internal_err_resp(f"Error: {props}")

        data = {
            "utc_time": str(props.utc_time)[:-7],
            "scenario_time": props.scenario_time,
        }
        return ok_resp(data)
