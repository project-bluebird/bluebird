"""
Provides logic for the 'eplog' (episode log file) API endpoint
"""

import os
from pathlib import Path

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.logging as bb_logging
from bluebird.api.resources.utils.utils import parse_args, sim_proxy
from bluebird.settings import in_agent_mode


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("close_ep", type=bool, location="args", required=False)


class EpLog(Resource):
    """
    Contains logic for the EPLOG endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events. Returns the current episode ID and log content
        """

        if not in_agent_mode():
            return responses.bad_request_resp(
                "Episode data only recorded when in Agent mode"
            )

        req_args = parse_args(_PARSER)
        close_ep = req_args.get("close_ep", False)

        ep_file_path = bb_logging.EP_FILE

        if not ep_file_path:
            return responses.bad_request_resp("No episode being recorded")

        if close_ep:
            err = sim_proxy().simulation.reset()
            if err:
                return responses.internal_err_resp(f"Could not reset simulation: {err}")

        full_ep_file = Path(os.getcwd(), ep_file_path)
        if not full_ep_file.exists():
            return responses.internal_err_resp(f"Could not find episode file")

        lines = list(line.rstrip("\n") for line in open(full_ep_file))

        data = {
            "cur_ep_id": bb_logging.EP_ID,
            "cur_ep_file": str(full_ep_file),
            "lines": lines,
        }

        return responses.ok_resp(data)
