"""
Tests for the ALT endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign, Altitude, VerticalSpeed

from tests.unit import API_PREFIX


def test_alt_post(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    resp = test_flask_client.post(f"{API_PREFIX}/alt")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {}
    resp = test_flask_client.post(f"{API_PREFIX}/alt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "TEST"
    data = {"acid": callsign}
    resp = test_flask_client.post(f"{API_PREFIX}/alt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"alt": 0}
    resp = test_flask_client.post(f"{API_PREFIX}/alt", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"acid": callsign}
    alt = Altitude(12300)
    for test_case in [alt.flight_levels, alt.feet]:
        data["alt"] = test_case
        resp = test_flask_client.post(f"{API_PREFIX}/alt", json=data)
        assert resp.status_code == HTTPStatus.OK
        cfl_args = utils.sim_proxy().last_cfl
        assert cfl_args, "Expected set_cleared_fl to be called"
        assert str(cfl_args["callsign"]) == callsign
        assert cfl_args["flight_level"] == alt

    data["vspd"] = 20
    resp = test_flask_client.post(f"{API_PREFIX}/alt", json=data)
    assert resp.status_code == HTTPStatus.OK
    cfl_args = utils.sim_proxy().last_cfl
    assert cfl_args, "Expected set_cleared_fl to be called"
    assert cfl_args["vspd"] == VerticalSpeed(20), ""


def test_alt_get(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the GET method
    """

    resp = test_flask_client.get(f"{API_PREFIX}/alt")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = Callsign("TEST")
    args = f"?acid={str(callsign)}"

    resp = test_flask_client.get(f"{API_PREFIX}/alt{args}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json[str(callsign)]["fl_current"] == 0
    assert resp.json[str(callsign)]["fl_cleared"] == 0
    assert resp.json[str(callsign)]["fl_requested"] == 0
