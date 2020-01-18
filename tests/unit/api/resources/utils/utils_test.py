"""
Tests functionality of the bluebird.api.resources.utils package
"""
from http import HTTPStatus

from flask import Response
from flask_restful import reqparse
from flask_restful import Resource

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
import bluebird.utils.properties as properties
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


def test_check_exists(monkeypatch):
    """Tests for check_exists"""

    class MockAircraftControls:
        def __init__(self):
            self._exists_called = False

        def exists(self, callsign: types.Callsign):
            assert isinstance(callsign, types.Callsign)
            if not self._exists_called:
                self._exists_called = True
                return "Invalid callsign"
            # "TEST*" aircraft exist, all others do not
            return str(callsign).upper().startswith("TEST")

    class MockSimProxy:
        @property
        def aircraft(self):
            return self._aircraft_controls

        def __init__(self):
            self._aircraft_controls = MockAircraftControls()

    mock = MockSimProxy()
    monkeypatch.setattr(utils, "sim_proxy", lambda: mock)

    callsign = types.Callsign("FAKE")

    # Test error handling

    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(callsign)
    assert isinstance(resp, Response)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert (
        resp.data.decode() == "Could not check if the aircraft exists: Invalid callsign"
    )

    # Test missing callsign

    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(callsign)
    assert isinstance(resp, Response)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    callsign = types.Callsign("TEST")

    # Test valid callsign

    with api.FLASK_APP.test_request_context():
        resp = utils.check_exists(callsign)
    assert not resp


def test_convert_aircraft_props():
    """Tests for convert_aircraft_props"""

    props = properties.AircraftProperties(
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

    callsign_str = "TEST"

    segments = [
        properties.RouteItem(
            types.Waypoint("WPT1", types.LatLon(0, 0), types.Altitude("FL350")),
            types.GroundSpeed(150),
        ),
        properties.RouteItem(
            types.Waypoint("WPT2", types.LatLon(0, 0), None), types.GroundSpeed(200),
        ),
        properties.RouteItem(
            types.Waypoint("WPT3", types.LatLon(0, 0), types.Altitude("FL370")), None
        ),
    ]
    route = properties.AircraftRoute(types.Callsign(callsign_str), segments, 1)

    converted = utils.convert_aircraft_route(route)
    assert isinstance(converted, dict)
    assert len(converted) == 1
    assert len(converted[callsign_str]) == 2

    assert converted[callsign_str]["current_segment_index"] == 1

    converted_route = converted[callsign_str]["route"]
    assert converted_route == [
        {"req_alt": 35000, "req_gspd": 492, "wpt_name": "WPT1"},
        {"req_alt": None, "req_gspd": 656, "wpt_name": "WPT2"},
        {"req_alt": 37000, "req_gspd": None, "wpt_name": "WPT3"},
    ]
