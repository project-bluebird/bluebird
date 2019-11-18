"""
Tests functionality of the bluebird.api.resources.utils package
"""

from http import HTTPStatus

from flask import Response
from flask_restful import Resource, reqparse

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties

from tests.unit import API_PREFIX


def test_parse_args_from_query_string(test_flask_client):
    """Tests for parse_args for URL query strings"""

    parser = reqparse.RequestParser()
    parser.add_argument("a", type=str, location="args", required=True)
    parser.add_argument("b", type=str, location="args", required=False)

    class Test(Resource):
        @staticmethod
        def get():
            utils.parse_args(parser)

    api.FLASK_API.add_resource(Test, "/test")

    endpoint = f"{API_PREFIX}/test"

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.OK


def test_try_parse_lat_lon():
    """Tests for try_parse_lat_lon"""

    test_data = [
        {},
        {"lat": "aa"},
        {"lat": 1, "lon": "aa"},
        {"lat": "aa", "lon": 1},
        {"lat": 91, "lon": 1},
        {"lat": 45, "lon": 181},
    ]

    for test_case in test_data:
        with api.FLASK_APP.test_request_context():
            res = utils.try_parse_lat_lon(test_case)
        assert isinstance(res, Response)
        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert res.data.decode().startswith("Invalid LatLon")

    args = {"lat": 45, "lon": 90}
    with api.FLASK_APP.test_request_context():
        res: types.LatLon = utils.try_parse_lat_lon(args)
    assert isinstance(res, types.LatLon)
    assert res.lat_degrees == args["lat"]
    assert res.lon_degrees == args["lon"]


def test_convert():
    """Tests for convert"""

    props = AircraftProperties(
        "A380",
        types.Altitude(18_500),
        types.Callsign("TEST"),
        types.Altitude("FL225"),
        types.GroundSpeed(23),
        types.Heading(47),
        types.LatLon(43.8, 123.4),
        types.Altitude(25_000),
        types.VerticalSpeed(32),
    )

    converted = utils.convert_aircraft_props(props)
    assert isinstance(converted, dict)
    assert len(converted) == 1

    converted_props = converted["TEST"]
    assert len(converted_props) == 9
    assert converted_props["actype"] == "A380"
    assert converted_props["cleared_fl"] == 22_500
    assert converted_props["current_fl"] == 18_500
    assert converted_props["gs"] == 23.0
    assert converted_props["hdg"] == 47
    assert converted_props["lat"] == 43.8
    assert converted_props["lon"] == 123.4
    assert converted_props["requested_fl"] == 25_000
    assert converted_props["vs"] == 32.0


def test_convert_aircraft_route():
    """Tests for convert_aircraft_route"""
    assert False, "NotImplemented"


def test_check_exists():
    """Tests for check_exists"""
    assert False, "NotImplemented"
