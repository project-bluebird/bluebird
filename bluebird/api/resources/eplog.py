"""
Provides logic for the 'eplog' (episode log file) API endpoint
"""

# TODO(rkm 2020-01-12) Remove the close_ep arg - mixed concerns

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
import bluebird.logging as bb_logging
from bluebird.settings import in_agent_mode


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("close_ep", type=bool, location="args", required=False)


class EpLog(Resource):
    """Contains logic for the EPLOG endpoint"""

    @staticmethod
    def get():
        """Logic for GET events. Returns the current episode ID and log content"""

        req_args = utils.parse_args(_PARSER)
        close_ep = req_args.get("close_ep", False)

        if not in_agent_mode():
            return responses.bad_request_resp(
                "Episode data only recorded when in Agent mode"
            )

        ep_file_path = bb_logging.EP_FILE

        if not ep_file_path:
            return responses.bad_request_resp("No episode being recorded")

        if close_ep:
            err = utils.sim_proxy().simulation.reset()
            if err:
                return responses.internal_err_resp(f"Couldn't reset simulation: {err}")

        if not ep_file_path.exists():
            return responses.internal_err_resp(f"Could not find episode file")

        lines = list(line.rstrip("\n") for line in open(ep_file_path))

        data = {
            "cur_ep_id": bb_logging.EP_ID,
            "cur_ep_file": str(ep_file_path.absolute()),
            "log": lines,
        }

        return responses.ok_resp(data)
