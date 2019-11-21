"""
Tests for the LISTROUTE endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftRoute, RouteItem

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockAircraftControls:
    # pylint: disable=missing-docstring
    def __init__(self):
        self._get_route_called = False

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def route(self, callsign: types.Callsign):  # -> Union[AircraftRoute, str]:
        assert isinstance(callsign, types.Callsign)
        if not self._get_route_called:
            self._get_route_called = True
            return "Error: Couldn't get route"
        segments = [
            RouteItem(types.Waypoint("FIX1", types.LatLon(45, 90), None), None),
            RouteItem(
                types.Waypoint("FIX2", types.LatLon(50, 95), types.Altitude(321)),
                types.GroundSpeed(123),
            ),
        ]
        return AircraftRoute(callsign, segments, 1)


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(MockAircraftControls(), None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_listroute_get(
    test_flask_client, _set_bb_app
):  # pylint: disable=unused-argument
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/listroute"
    callsign_label = api_utils.CALLSIGN_LABEL

    # Test arg parsing

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign_str = "A"
    resp = test_flask_client.get(f"{endpoint}?{callsign_label}={callsign_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert callsign_label in resp.json["message"]

    # Test aircraft exists check

    callsign_str = "AAA"
    resp = test_flask_client.get(f"{endpoint}?{callsign_label}={callsign_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f'Aircraft "{callsign_str}" does not exist'

    # Test get_route

    callsign_str = "TEST"
    resp = test_flask_client.get(f"{endpoint}?{callsign_label}={callsign_str}")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't get route"

    resp = test_flask_client.get(f"{endpoint}?{callsign_label}={callsign_str}")
    assert resp.status_code == HTTPStatus.OK

    assert resp.json == {
        "TEST": {
            "route": [
                {"req_alt": None, "req_gspd": None, "wpt_name": "FIX1"},
                {"req_alt": 321, "req_gspd": 403, "wpt_name": "FIX2"},
            ],
            "current_segment_index": 1,
        }
    }
