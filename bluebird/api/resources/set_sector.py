"""
Provides logic for the set sector endpoint
"""

from http import HTTPStatus
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.sector_validation import validate_geojson_sector
from bluebird.api.resources.utils.utils import sim_proxy, parse_args


_PARSER = reqparse.RequestParser()
# _PARSER.add_argument("sector_name", type=str, location="json", required=True)
_PARSER.add_argument("content", type=dict, location="json", required=True)


class SetSector(Resource):
    """Contains logic for the upload sector endpoint"""

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = parse_args(_PARSER)

        # sector_name = req_args["sector_name"]

        # if not sector_name:
        #     return responses.bad_request_resp("Sector name must be provided")

        content = req_args["content"]

        err = validate_geojson_sector(content)
        if err:
            return responses.bad_request_resp(f"Invalid scenario content: {err}")

        # Keep track of the uploaded sector in the SimProxy.
        sim_proxy().sector = content

        # err = sim_proxy().simulation.upload_new_sector(sector_name, content)

        return responses.checked_resp(None, HTTPStatus.CREATED)
