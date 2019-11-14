"""
Tests for the CRE endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils
from bluebird.utils.types import Callsign, Altitude, GroundSpeed, Heading, LatLon

from tests.unit import API_PREFIX
from tests.unit.api import TEST_LAT, TEST_LON


def test_cre_post(test_flask_client, patch_bb_app):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/cre"

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    callsign = "T"
    data = {utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    callsign = "XXX"
    data = {utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "type" in resp.json["message"]

    data["type"] = ""
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "lat" in resp.json["message"]

    data["lat"] = 91
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "lon" in resp.json["message"]

    data["lon"] = 181
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "hdg" in resp.json["message"]

    data["hdg"] = "aaa"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["hdg"] == "Heading must be an int"

    data["hdg"] = 123
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = -1
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["alt"] == "Altitude must be positive"

    data["alt"] = "FL100"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "spd" in resp.json["message"]

    data["spd"] = "..."
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["spd"] == "Ground speed must be an int"

    # Test aircraft exists

    data = {
        utils.CALLSIGN_LABEL: "TEST1",
        "type": "A380",
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "hdg": 123,
        "alt": 18_500,
        "spd": 50,
    }
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft TEST1 already exists"

    # Test LatLon parse

    data[utils.CALLSIGN_LABEL] = "XXX"
    data["lat"] = -91
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid LatLon")

    # Test valid aircraft creation

    data["lat"] = TEST_LAT
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.CREATED

    created_aircraft = utils.sim_client().aircraft.created_aricraft
    assert len(created_aircraft) == len(data) - 1
    assert created_aircraft[0] == Callsign(data[utils.CALLSIGN_LABEL])
    assert created_aircraft[1] == data["type"]
    assert created_aircraft[2] == LatLon(data["lat"], data["lon"])
    assert created_aircraft[3] == Heading(data["hdg"])
    assert created_aircraft[4] == Altitude(data["alt"])
    assert created_aircraft[5] == GroundSpeed(data["spd"])
