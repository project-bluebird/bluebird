"""
Provides logic for the shutdown endpoint
"""

from flask import request
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import internal_err_resp, ok_resp
from bluebird.api.resources.utils.utils import parse_args, sim_proxy


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("stop_sim", type=bool, location="args", required=False)


class Shutdown(Resource):
    """
    Contains logic for the shutdown endpoint
    """

    @staticmethod
    def post():
        """
        Shuts down the BlueBird server
        :return:
        """

        req_args = parse_args(_PARSER)

        sim_quit_msg = ""
        if req_args.get("stop_sim", False):
            sim_quit = sim_proxy().stop_sim(shutdown_sim=True)
            sim_quit_msg = f". (Sim exited ok: {sim_quit})"

        try:
            # TODO Check we still get a response before this executes. If not, need to
            # set this to fire on a timer
            request.environ.get("werkzeug.server.shutdown")()
        except Exception as exc:  # pylint: disable=broad-except
            return internal_err_resp(f"Could not shutdown: {exc}{sim_quit_msg}")

        data = {"msg": f"Shutting down{sim_quit_msg}"}
        return ok_resp(data)
