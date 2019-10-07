"""
Provides logic for the POS (position) API endpoint
"""

from dataclasses import asdict

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, ok_resp
from bluebird.api.resources.utils.utils import CALLSIGN_LABEL, parse_args, sim_proxy
from bluebird.utils.types import Callsign


_PARSER = reqparse.RequestParser()
# TODO This needs changed to accept multiple (comma-separated) callsigns again
_PARSER.add_argument(CALLSIGN_LABEL, type=Callsign, location="args", required=True)


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
        callsign_strings = req_args[CALLSIGN_LABEL]

        # TODO Update API docs

        if callsign_strings.upper() == "ALL":
            props, sim_t = sim_proxy().get_all_aircraft_props()
            if not props:
                return bad_request_resp("No aircraft in the simulation")
            # TODO Check this
            data = {}
            for prop in props:
                data[prop.callsign] = asdict(prop)
                del data[prop.callsign]["callsign"]
            data["sim_t"] = sim_t
            return ok_resp(data)

        try:
            # TODO Test cases for the string split
            callsigns = map(Callsign, callsign_strings.split(","))
        except AssertionError as exc:
            return bad_request_resp(f"Invalid callsign: {exc}")

        data = {}
        for callsign in callsigns:
            if not sim_proxy().contains(callsign):
                return bad_request_resp(f"Aircraft {callsign} not found")
            props, sim_t = sim_proxy().get_aircraft_props(callsign)
            data[callsign] = asdict(props)
            del data[props.callsign]["callsign"]
            data["sim_t"] = sim_t

        return ok_resp(data)
