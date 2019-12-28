"""
Provides logic for the sector API endpoint
"""

from http import HTTPStatus

from aviary.sector.sector_element import SectorElement
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.sector_validation import validate_geojson_sector

# Note (RKM 2019-12-20) Have to avoid the name collision with the class below
from bluebird.sim_proxy.sim_proxy import Sector as Proxy_Sector


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="json", required=True)
_PARSER.add_argument("content", type=dict, location="json", required=True)


class Sector(Resource):
    """
    Contains logic for the SECTOR endpoint
    """

    @staticmethod
    def get():
        """Returns the sector defined in the current simulation"""

        sector: Proxy_Sector = utils.sim_proxy().sector

        if not sector:
            return responses.bad_request_resp("No sector has been set")

        # TODO (RKM 2019-12-20) Check what exceptions this can throw
        try:
            geojson = sector.element.sector_geojson()
        except Exception as exc:
            return responses.internal_err_resp(f"Couldn't get sector geojson: {exc}")

        return responses.ok_resp({"name": sector.name, "content": geojson})

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = utils.parse_args(_PARSER)

        sector_name = req_args["name"]

        if not sector_name:
            return responses.bad_request_resp("Sector name must be provided")

        sector = validate_geojson_sector(req_args["content"])
        if not isinstance(sector, SectorElement):
            return responses.bad_request_resp(f"Invalid scenario content: {sector}")

        err = utils.sim_proxy().set_sector(Proxy_Sector(sector_name, sector))
        return responses.checked_resp(err, HTTPStatus.CREATED)
