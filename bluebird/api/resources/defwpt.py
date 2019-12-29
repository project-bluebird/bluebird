"""
Provides logic for the DEFWPT (define waypoint) API endpoint
"""

import logging
from http import HTTPStatus

from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import LatLon


_LOGGER = logging.getLogger(__name__)

# TODO Maybe add altitude as an optional arg
_PARSER = reqparse.RequestParser()
_PARSER.add_argument("wpname", type=str, location="json", required=True)
_PARSER.add_argument("lat", type=float, location="json", required=True)
_PARSER.add_argument("lon", type=float, location="json", required=True)
_PARSER.add_argument("type", type=str, location="json", required=False)


class DefWpt(Resource):
    """
    DEFWPT (define waypoint) command
    """

    @staticmethod
    def post():
        """
        Logic for POST events. If the request contains valid waypoint information, then
        a request is sent to the simulator to create it.
        :return:
        """

        req_args = utils.parse_args(_PARSER)

        wp_name = req_args["wpname"]
        if not wp_name:
            return responses.bad_request_resp("Waypoint name must be provided")

        position = utils.try_parse_lat_lon(req_args)
        if not isinstance(position, LatLon):
            return position

        err = utils.sim_proxy().waypoints.define(
            wp_name, position, type=req_args["type"]
        )

        return responses.checked_resp(err, HTTPStatus.CREATED)
