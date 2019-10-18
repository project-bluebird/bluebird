"""
SimInfo endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils.responses import ok_resp, internal_err_resp
from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.settings import Settings


class SimInfo(Resource):
    @staticmethod
    def get():

        try:
            sim_props = sim_proxy().sim_properties
            callsigns = [
                str(x.callsign) for x in sim_proxy().get_all_aircraft_props()[0]
            ]
        except Exception as exc:
            return internal_err_resp(f"Error reading data from sim: {exc}")

        data = {
            "callsigns": callsigns,
            "mode": Settings.SIM_MODE.name,
            "scn_name": sim_props.scn_name,
            "sim_speed": sim_props.speed,
            "sim_state": sim_props.state.name,
            "sim_time": sim_props.time,
            "sim_type": Settings.SIM_TYPE.name,
            "step_size": sim_props.step_size,
        }

        return ok_resp(data)
