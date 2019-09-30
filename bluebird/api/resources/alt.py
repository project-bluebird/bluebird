"""
Provides logic for the ALT (altitude) API endpoint
"""

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.listroute import parse_route_data
from bluebird.api.resources.utils import (
    bb_app,
    check_acid,
    generate_arg_parser,
    process_stack_cmd,
)

REQ_ARGS = ["alt"]
OPT_ARGS = ["vspd"]
PARSER = generate_arg_parser(REQ_ARGS, OPT_ARGS)

# Parser for get requests
PARSER_GET = reqparse.RequestParser()
PARSER_GET.add_argument("acid", type=str, location="args", required=True)


class Alt(Resource):
    """
    BlueSky ALT (altitude) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains an existing aircraft ID, then a request is sent
        to alter its altitude.
        :return: :class:`~flask.Response`
        """

        parsed = PARSER.parse_args(strict=True)
        acid = parsed["acid"]
        fl_cleared = parsed["alt"]
        vspd = parsed["vspd"] if parsed["vspd"] else ""

        resp = check_acid(acid)
        if resp is not None:
            return resp

        fl_cleared_feet_or_fl = fl_cleared

        # Parse FL to meters
        if fl_cleared.upper().startswith("FL"):
            fl_cleared = round(int(fl_cleared[2:]) * 100 * 0.3048)

        bb_app().ac_data.cleared_fls.update({acid: fl_cleared})

        cmd_str = f"ALT {acid} {fl_cleared_feet_or_fl} {vspd}".strip()
        return process_stack_cmd(cmd_str)

    @staticmethod
    def get():
        """
        Logic for GET events. If the request contains an identifier to an existing aircraft,
        then its current, requested, and cleared flight levels are returned (if they can be
        determined).
        :return: :class:`~flask.Response`
        """

        parsed = PARSER_GET.parse_args()
        acid = parsed["acid"]

        if not bb_app().ac_data.store:
            resp = jsonify("No aircraft in the simulation")
            resp.status_code = 400
            return resp

        if check_acid(acid):
            resp = jsonify("Invalid ACID, or the aircraft does not exist")
            resp.status_code = 400
            return resp

        # Current flight level
        fl_current = bb_app().ac_data.get(acid)[acid]["alt"]

        # Cleared flight level
        fl_cleared = bb_app().ac_data.cleared_fls.get(acid)
        if fl_cleared:
            fl_cleared = int(fl_cleared)

        # Requested flight level
        fl_requested = None
        cmd_str = f"LISTRTE {acid}"
        reply = bb_app().sim_client.send_stack_cmd(cmd_str, response_expected=True)

        if reply and isinstance(reply, list):
            parsed_route = parse_route_data(reply)
            if isinstance(parsed_route, list):
                for part in parsed_route:
                    if part["is_current"]:
                        fl_requested = part["req_alt"]

        if isinstance(fl_requested, str):
            fl_requested = round(int(fl_requested[2:]) * 100 * 0.3048)

        resp = jsonify(
            {
                "fl_current": fl_current,
                "fl_cleared": fl_cleared,
                "fl_requested": fl_requested,
            }
        )
        resp.status_code = 200
        return resp
