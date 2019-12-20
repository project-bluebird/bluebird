"""
Provides logic for the sector API endpoint
"""

from http import HTTPStatus

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.sector_validation import validate_geojson_sector


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("content", type=dict, location="json", required=True)


class Sector(Resource):
    """
    Contains logic for the SECTOR endpoint
    """

    @staticmethod
    def get():
        """Returns the sector defined in the current simulation"""

        if not hasattr(utils.sim_proxy(), "sector"):
            return responses.internal_err_resp("No sector has been set")

        sector = utils.sim_proxy().sector

        return responses.ok_resp({"sector": sector})

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = utils.parse_args(_PARSER)

        # sector_name = req_args["sector_name"]

        # if not sector_name:
        #     return responses.bad_request_resp("Sector name must be provided")

        content = req_args["content"]

        err = validate_geojson_sector(content)
        if err:
            return responses.bad_request_resp(f"Invalid scenario content: {err}")

        # Keep track of the uploaded sector in the SimProxy.
        utils.sim_proxy().sector = content

        # err = sim_proxy().simulation.upload_new_sector(sector_name, content)

        # TODO
        data = None
        return responses.checked_resp(data, HTTPStatus.CREATED)
