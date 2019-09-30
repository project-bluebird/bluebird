"""
Provides logic for the shutdown endpoint
"""

from flask import jsonify, request
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app

PARSER = reqparse.RequestParser()
PARSER.add_argument("stop_sim", type=bool, location="args", required=False)


class Shutdown(Resource):
    """
    Contains logic for the shutdown endpoint
    """

    @staticmethod
    def post():
        """
        Shuts down the BlueBird server
        :return: :class:`~flask.Response`
        """

        parsed = PARSER.parse_args(strict=True)
        stop_sim = not parsed["stop_sim"] is None

        sim_quit_msg = ""
        if stop_sim:
            sim_quit = bb_app().sim_client.quit()
            sim_quit_msg = f". (Sim exited ok: {sim_quit})"

        try:
            request.environ.get("werkzeug.server.shutdown")()
        except Exception as exc:  # pylint: disable=W0703
            resp = jsonify(f"Could not shutdown: {exc}{sim_quit_msg}")
            resp.status_code = 500
            return resp

        resp = jsonify(f"Shutting down{sim_quit_msg}")
        resp.status_code = 200
        return resp
