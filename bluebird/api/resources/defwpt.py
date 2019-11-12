"""
Provides logic for the DEFWPT (define waypoint) API endpoint
"""

from http import HTTPStatus
import logging

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils.responses import bad_request_resp, checked_resp
from bluebird.api.resources.utils.utils import parse_args, try_parse_lat_lon, sim_proxy
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

        req_args = parse_args(_PARSER)

        wp_name = req_args["wpname"]
        if not wp_name:
            return bad_request_resp("Waypoint name must be provided")

        position = try_parse_lat_lon(req_args)
        if not isinstance(position, LatLon):
            return position

        err = sim_proxy().define_waypoint(wp_name, position, type=req_args["type"])

        return bad_request_resp(err) if err else checked_resp(err, HTTPStatus.CREATED)
