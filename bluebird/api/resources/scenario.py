"""
Provides logic for the scenario (create scenario) API endpoint
"""

import logging

from flask import jsonify
from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import bb_app, validate_scenario, wait_until_eq
from bluebird.logging import store_local_scn

_LOGGER = logging.getLogger("bluebird")

PARSER = reqparse.RequestParser()
PARSER.add_argument("scn_name", type=str, location="json", required=True)
PARSER.add_argument(
    "content", type=str, location="json", required=True, action="append"
)
PARSER.add_argument("start_new", type=bool, location="json", required=False)
PARSER.add_argument("start_dtmult", type=float, location="json", required=False)


class Scenario(Resource):
    """
	Contains logic for the scenario endpoint
	"""

    @staticmethod
    def post():
        """
		Logic for POST events.
		:return: :class:`~flask.Response`
		"""

        parsed = PARSER.parse_args()

        scn_name = scn_base = parsed["scn_name"]

        if not scn_name.endswith(".scn"):
            scn_name += ".scn"

        if scn_name.startswith("scenario"):
            scn_name = scn_name[len("scenario") + 1 :]

        content = parsed["content"]
        err = validate_scenario(content)

        if err:
            resp = jsonify(f"Invalid scenario content: {err}")
            resp.status_code = 400
            return resp

        store_local_scn(scn_name, content)

        err = bb_app().sim_client.upload_new_scenario(scn_name, content)

        if err:
            resp = jsonify(f"Error uploading scenario: {err}")
            resp.status_code = 500

        elif parsed["start_new"]:

            dtmult = parsed["start_dtmult"] if parsed["start_dtmult"] else 1.0
            err = bb_app().sim_client.load_scenario(scn_name, speed=dtmult)

            if err:
                resp = jsonify(f"Could not start scenario after upload: {err}")
                resp.status_code = 500
                return resp

            if not wait_until_eq(bb_app().ac_data.store, True):
                resp = jsonify(
                    "No aircraft data received after loading. Scenario might not contain any "
                    "aircraft"
                )
                resp.status_code = 500
                return resp

            resp = jsonify(f"Scenario {scn_base} uploaded and started")
            resp.status_code = 200

        else:
            resp = jsonify(f"Scenario {scn_base} uploaded")
            resp.status_code = 201

        return resp
