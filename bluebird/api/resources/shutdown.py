"""
Provides logic for the shutdown endpoint
"""
from flask import request
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("stop_sim", type=bool, location="args", required=False)


class Shutdown(Resource):
    """Contains logic for the shutdown endpoint"""

    @staticmethod
    def post():
        """Shuts down the BlueBird server"""

        req_args = utils.parse_args(_PARSER)

        sim_quit = utils.sim_proxy().shutdown(shutdown_sim=bool(req_args["stop_sim"]))
        sim_quit_msg = f"(Sim shutdown ok = {sim_quit})"

        # TODO Check we still get a response before this executes. If not, need to set
        # this to fire on a timer
        try:
            shutdown_fn = request.environ.get("werkzeug.server.shutdown")
            if not shutdown_fn:
                return responses.internal_err_resp(
                    f"No shutdown function available. {sim_quit_msg}"
                )
            shutdown_fn()
        except Exception as exc:
            return responses.internal_err_resp(
                f"Could not shutdown: {exc}. {sim_quit_msg}"
            )

        data = f"BlueBird shutting down! {sim_quit_msg}"
        return responses.ok_resp(data)
