"""
Provides logic for the sector API endpoint
"""

from http import HTTPStatus

from aviary.sector.sector_element import SectorElement
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import Sector as SectorWrapper
from bluebird.utils.sector_validation import validate_geojson_sector


_PARSER = reqparse.RequestParser()
_PARSER.add_argument("name", type=str, location="json", required=True)
_PARSER.add_argument("content", type=dict, location="json", required=False)


class Sector(Resource):
    """Contains logic for the SECTOR endpoint"""

    @staticmethod
    def get():
        """Returns the sector defined in the current simulation"""

        sector: SectorWrapper = utils.sim_proxy().sector

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
        """Upload a new sector definition"""

        req_args = utils.parse_args(_PARSER)

        sector_name = req_args["name"]

        if not sector_name:
            return responses.bad_request_resp("Sector name must be provided")

        sector = req_args["content"]

        if sector:
            sector = validate_geojson_sector(req_args["content"])
            if not isinstance(sector, SectorElement):
                return responses.bad_request_resp(f"Invalid sector content: {sector}")
        else:
            # NOTE(rkm 2020-01-03) Have to set this to none, since an empty dict may
            # have been passed, which doesn't match the type of Optional[SectorElement]
            sector = None

        sector = SectorWrapper(sector_name, sector)
        err = utils.sim_proxy().simulation.load_sector(sector)

        return responses.checked_resp(err, HTTPStatus.CREATED)
