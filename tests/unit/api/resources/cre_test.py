"""
Tests for the CRE endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.responses as responses
import bluebird.api.resources.utils.utils as utils

from tests.unit import API_PREFIX


def test_cre_post(test_flask_client):
    """Tests the POST method"""

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

    callsign = "AAA"
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
    assert "gspd" in resp.json["message"]

    data["gspd"] = "..."
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json["message"]["gspd"] == "Ground speed must be numeric"

    with mock.patch("bluebird.api.resources.cre.utils", wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL

        # Test response when aircraft exists

        with api.FLASK_APP.test_request_context():
            response = responses.bad_request_resp("Missing aircraft")

        utils_patch.check_exists.return_value = response

        data = {
            utils.CALLSIGN_LABEL: "TEST1",
            "type": "",
            "lat": "1.23",
            "lon": "4.56",
            "hdg": 123,
            "alt": 18_500,
            "gspd": 50,
        }

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test LatLon parse

        utils_patch.check_exists.return_value = None

        data[utils.CALLSIGN_LABEL] = "AAA"
        data["lat"] = -91

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("Invalid LatLon")

        # Test type check

        data["lat"] = 0
        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("Aircraft type must be specified")

        # Test error response from aircraft creation

        mock_proxy = mock.MagicMock()
        utils_patch.sim_proxy.return_value = mock_proxy

        mock_proxy.aircraft.create.return_value = "Couldn't create aircraft"

        data["type"] = "TEST"

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't create aircraft"

        # Test valid aircraft creation

        mock_proxy.aircraft.create.return_value = None

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.CREATED
