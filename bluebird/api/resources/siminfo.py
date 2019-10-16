"""
SimInfo endpoint
"""

import traceback

from flask_restful import Resource

from bluebird.api.resources.utils.responses import ok_resp, internal_err_resp
from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.settings import Settings


class SimInfo(Resource):
    @staticmethod
    def get():

        # TODO Better error handling
        try:
            sim_props = sim_proxy().sim_properties
            callsigns = [
                str(x.callsign) for x in sim_proxy().get_all_aircraft_props()[0]
            ]
        except Exception:
            return internal_err_resp(traceback.format_exc())

        data = {
            "sim_state": sim_props.state,
            "sim_speed": sim_props.speed,
            "step_size": sim_props.step_size,
            "sim_time": sim_props.time,
            "callsigns": callsigns,
            "scn_name": sim_props.scn_name,
            "mode": Settings.SIM_MODE.name,
        }

        return ok_resp(data)
