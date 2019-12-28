"""
Tests for the POS endpoint
"""

import datetime
from http import HTTPStatus

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types
from bluebird.utils.properties import SimProperties, SimState, AircraftProperties

from tests.unit import API_PREFIX

_ENDPOINT = f"{API_PREFIX}/pos"


class MockAircraftControls:
    @property
    def all_properties(self):
        if not self._get_properties_called:
            self._get_properties_called = True
            return "Error"
        all_props = {}
        for i in range(2):
            props = self.properties(types.Callsign(f"TEST{i}"))
            all_props[str(props.callsign)] = props
        return all_props

    def __init__(self):
        self._get_properties_called = False

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def properties(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        if not self._get_properties_called:
            self._get_properties_called = True
            return "Invalid callsign"
        return AircraftProperties(
            "A380",
            types.Altitude(18_500),
            callsign,
            types.Altitude(22_000),
            types.GroundSpeed(53),
            types.Heading(74),
            types.LatLon(51.529761, -0.127531),
            types.Altitude(25_300),
            types.VerticalSpeed(73),
        )


class MockSimulatorControls:
    @property
    def properties(self):
        if not self._props_called:
            self._props_called = True
            return "Error: Couldn't get the sim properties"
        return SimProperties(
            scenario_name="TEST",
            scenario_time=123.45,
            seed=0,
            speed=0,
            state=SimState.INIT,
            step_size=1.0,
            utc_time=datetime.datetime.now(),
        )

    def __init__(self):
        self._props_called = False


def test_pos_get_single(test_flask_client, _set_bb_app):
    """Tests the GET method with a single aircraft"""

    arg_str = f"{_ENDPOINT}?{api_utils.CALLSIGN_LABEL}"

    callsign = ""
    resp = test_flask_client.get(f"{arg_str}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert api_utils.CALLSIGN_LABEL in resp.json["message"]

    callsign = "FAKE"
    resp = test_flask_client.get(f"{arg_str}={callsign}")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't get the sim properties"

    resp = test_flask_client.get(f"{arg_str}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    callsign = "TEST"
    resp = test_flask_client.get(f"{arg_str}={callsign}")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Invalid callsign"

    resp = test_flask_client.get(f"{arg_str}={callsign}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {
        "TEST": {
            "actype": "A380",
            "cleared_fl": 22000,
            "current_fl": 18500,
            "gs": 53,
            "hdg": 74,
            "lat": 51.529761,
            "lon": -0.127531,
            "requested_fl": 25300,
            "vs": 73,
        },
        "scenario_time": 123.45,
    }


def test_pos_get_all(test_flask_client, _set_bb_app):
    """Tests the GET method with all aircraft"""

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't get the sim properties"

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Couldn't get all the aircraft properties: Error"

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {
        "TEST0": {
            "actype": "A380",
            "cleared_fl": 22000,
            "current_fl": 18500,
            "gs": 53,
            "hdg": 74,
            "lat": 51.529761,
            "lon": -0.127531,
            "requested_fl": 25300,
            "vs": 73,
        },
        "TEST1": {
            "actype": "A380",
            "cleared_fl": 22000,
            "current_fl": 18500,
            "gs": 53,
            "hdg": 74,
            "lat": 51.529761,
            "lon": -0.127531,
            "requested_fl": 25300,
            "vs": 73,
        },
        "scenario_time": 123.45,
    }
