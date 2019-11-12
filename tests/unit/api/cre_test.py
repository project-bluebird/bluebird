"""
Tests for the CRE endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX
from tests.unit.api import TEST_LAT, TEST_LON


def test_cre_post(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    resp = test_flask_client.post(f"{API_PREFIX}/cre")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {}
    resp = test_flask_client.post(f"{API_PREFIX}/cre", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "acid" in resp.json["message"]

    callsign = "TEST"
    data = {"acid": callsign}
    resp = test_flask_client.post(f"{API_PREFIX}/cre", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "type" in resp.json["message"]

    data = {
        "acid": callsign,
        "type": "A380",
        "lat": TEST_LAT,
        "lon": TEST_LON,
        "hdg": 123,
        "alt": 18_500,
        "spd": 50,
    }
    resp = test_flask_client.post(f"{API_PREFIX}/cre", json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "Aircraft TEST already exists" == resp.data.decode()

    data["acid"] = "ZZZZ"
    resp = test_flask_client.post(f"{API_PREFIX}/cre", json=data)
    assert resp.status_code == HTTPStatus.CREATED
