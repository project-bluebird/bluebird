"""
Provides logic for the 'eplog' (episode log file) API endpoint
"""

import os

from flask_restful import Resource, reqparse

import bluebird.logging as bb_logging
from bluebird.api.resources.utils import (
    sim_client,
    parse_args,
    bad_request_resp,
    internal_err_resp,
    ok_resp,
)

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("close_ep", type=bool, location="args", required=False)


class EpLog(Resource):
    """
    Contains logic for the eplog endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events.
        :return: :class:`~flask.Response`
        """

        req_args = parse_args(_PARSER)
        close_ep = req_args.get("close_ep", False)

        ep_file_path = bb_logging.EP_FILE

        if not ep_file_path:
            return bad_request_resp("No episode being recorded")

        if close_ep:
            err = sim_client().reset_sim()
            if err:
                return internal_err_resp(f"Could not reset simulation: {err}")

        full_ep_file = os.path.join(os.getcwd(), ep_file_path)
        lines = tuple(line.rstrip("\n") for line in open(full_ep_file))

        data = {
            "cur_ep_id": bb_logging.EP_ID,
            "cur_ep_file": full_ep_file,
            "lines": lines,
        }

        return ok_resp(data)
