"""
Provides logic for the epinfo (episode info) API endpoint
"""

import os

from flask_restful import Resource
from bluebird.api.resources.utils import bad_request_resp, ok_resp

import bluebird.logging as bb_logging


class EpInfo(Resource):
    """
    Contains logic for the epinfo endpoint
    """

    @staticmethod
    def get():
        """
        Logic for GET events
        :return:
        """

        current_ep_file = bb_logging.EP_FILE
        if not current_ep_file:
            return bad_request_resp("No episode being recorded")

        cwd = os.getcwd()
        full_log_dir = os.path.join(cwd, bb_logging.INST_LOG_DIR)
        full_ep_file = os.path.join(cwd, current_ep_file)

        data = {
            "inst_id": bb_logging.INSTANCE_ID,
            "cur_ep_id": bb_logging.EP_ID,
            "cur_ep_file": full_ep_file,
            "log_dir": full_log_dir,
        }

        return ok_resp(data)
