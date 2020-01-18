"""
Provides logic for the POS (position) API endpoint
"""

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.responses import internal_err_resp
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import SimProperties, AircraftProperties
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(
    utils.CALLSIGN_LABEL, type=Callsign, location="args", required=False
)


class Pos(Resource):
    """POS (position) command"""

    @staticmethod
    def get():
        """Logic for GET events. Returns properties for the specified aircraft"""

        req_args = utils.parse_args(_PARSER)
        callsign = req_args[utils.CALLSIGN_LABEL]

        sim_props = utils.sim_proxy().simulation.properties
        if not isinstance(sim_props, SimProperties):
            return responses.internal_err_resp(sim_props)

        if callsign:
            resp = utils.check_exists(utils.sim_proxy(), callsign)
            if resp:
                return resp

            props = utils.sim_proxy().aircraft.properties(callsign)
            if not isinstance(props, AircraftProperties):
                return internal_err_resp(props)

            data = utils.convert_aircraft_props(props)
            data.update({"scenario_time": sim_props.scenario_time})

            return responses.ok_resp(data)

        # else: get_all_properties

        props = utils.sim_proxy().aircraft.all_properties
        if isinstance(props, str):
            return responses.internal_err_resp(
                f"Couldn't get the aircraft properties: {props}"
            )
        if not props:
            return responses.bad_request_resp("No aircraft in the simulation")

        data = {}
        for prop in props.values():
            data.update(utils.convert_aircraft_props(prop))
        data["scenario_time"] = sim_props.scenario_time

        return responses.ok_resp(data)
