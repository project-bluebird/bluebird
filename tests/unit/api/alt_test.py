"""
Tests for the ALT endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Altitude, VerticalSpeed

from tests.unit import API_PREFIX


_ENDPOINT = f"{API_PREFIX}/alt"


def test_alt_post(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "T"
    data = {utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data = {utils.CALLSIGN_LABEL: "TEST", "alt": -1}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = 0
    data["vspd"] = "..."
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "vspd" in resp.json["message"]

    # Test correct units

    callsign = "TEST"
    data = {utils.CALLSIGN_LABEL: callsign}
    alt = Altitude(12300)
    for test_case in [alt.flight_levels, alt.feet]:
        data["alt"] = test_case
        resp = test_flask_client.post(_ENDPOINT, json=data)
        assert resp.status_code == HTTPStatus.OK
        cfl_args = utils.sim_proxy().last_cfl
        assert cfl_args, "Expected set_cleared_fl to be called"
        assert str(cfl_args["callsign"]) == callsign
        assert cfl_args["flight_level"] == alt

    # Test optional arg passed to set_cleared_fl

    data["vspd"] = 20
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK
    cfl_args = utils.sim_proxy().last_cfl
    assert cfl_args, "Expected set_cleared_fl to be called"
    assert cfl_args["vspd"] == VerticalSpeed(20), ""


def test_alt_get(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the GET method
    """

    # Test arg parsing

    resp = test_flask_client.get(f"{_ENDPOINT}?")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "T"
    resp = test_flask_client.get(f"{_ENDPOINT}?{utils.CALLSIGN_LABEL}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    # Test aircraft exists check

    callsign = "XXX"
    resp = test_flask_client.get(f"{_ENDPOINT}?{utils.CALLSIGN_LABEL}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft XXX not found"

    # Test response units

    callsign = "TEST"
    args = f"?{utils.CALLSIGN_LABEL}={callsign}"

    resp = test_flask_client.get(f"{_ENDPOINT}{args}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json[callsign]["fl_current"] == 18_500
    assert resp.json[callsign]["fl_cleared"] == 22_000
    assert resp.json[callsign]["fl_requested"] == 25_300
