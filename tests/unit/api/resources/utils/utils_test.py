"""
Tests functionality of the bluebird.api.resources.utils package
"""
from http import HTTPStatus

import mock
from flask import Response
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
import bluebird.utils.properties as props
import bluebird.utils.types as types
from tests.unit.api.resources import endpoint_path


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

    endpoint = endpoint_path("test")

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.get(f"{endpoint}?a=")
    assert resp.status_code == HTTPStatus.OK

    resp = test_flask_client.get(f"{endpoint}?a=&b=")
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


def test_check_exists():
    """Tests for check_exists"""

    sim_pros_mock = mock.Mock()
    callsign = types.Callsign("FAKE")

    # Test error handling

    sim_pros_mock.aircraft.exists.return_value = "Error"
    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(sim_pros_mock, callsign)
    assert isinstance(resp, Response)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Could not check if the aircraft exists: Error"

    # Test missing callsign

    sim_pros_mock.aircraft.exists.return_value = False
    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(sim_pros_mock, callsign)
    assert isinstance(resp, Response)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    callsign = types.Callsign("TEST")

    # Test valid callsign

    sim_pros_mock.aircraft.exists.return_value = True
    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(sim_pros_mock, callsign)
    assert not resp


def test_convert_aircraft_props():
    """Tests for convert_aircraft_props"""

    ac_props = props.AircraftProperties(
        aircraft_type="A380",
        altitude=types.Altitude(18_500),
        callsign=types.Callsign("TEST"),
        cleared_flight_level=types.Altitude("FL225"),
        ground_speed=types.GroundSpeed(23),
        heading=types.Heading(47),
        initial_flight_level=types.Altitude(18_500),
        position=types.LatLon(43.8, 123.4),
        requested_flight_level=types.Altitude(25_000),
        route_name=None,
        vertical_speed=types.VerticalSpeed(32),
    )

    converted = utils.convert_aircraft_props(ac_props)
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
