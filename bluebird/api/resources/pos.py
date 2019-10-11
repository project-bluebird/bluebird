"""
Provides logic for the POS (position) API endpoint
"""

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, ok_resp
from bluebird.api.resources.utils.utils import (
    CALLSIGN_LABEL,
    parse_args,
    sim_proxy,
    convert,
)
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=False)


class Pos(Resource):
    """
    BlueSky POS (position) command
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Returns properties for the specified aircraft
        :return:
        """

        req_args = parse_args(_PARSER)
        callsign = req_args[CALLSIGN_LABEL]

        # TODO Update API docs
        if not callsign:
            props, sim_t = sim_proxy().get_all_aircraft_props()
            if not props:
                return bad_request_resp("No aircraft in the simulation")

            data = {}
            for prop in props:
                data.update(convert(prop))
            data["sim_t"] = sim_t

            return ok_resp(data)

        # TODO: Refactor the None check to be here instead of using contains(...)
        if not sim_proxy().contains(callsign):
            return bad_request_resp(f"Aircraft {callsign} was not found")

        props, sim_t = sim_proxy().get_aircraft_props(callsign)
        
        data = {**convert(props), "sim_t": sim_t}

        return ok_resp(data)
