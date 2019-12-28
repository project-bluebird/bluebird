"""
Tests for the ALT endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp

from tests.unit import API_PREFIX
from tests.unit.api.resources import patch_path, TEST_AIRCRAFT_PROPS


_ENDPOINT = "alt"
_ENDPOINT_PATH = f"{API_PREFIX}/{_ENDPOINT}"


def test_alt_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    data = {}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign = "X"
    data = {utils.CALLSIGN_LABEL: callsign}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data = {utils.CALLSIGN_LABEL: "TEST", "alt": -1}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "alt" in resp.json["message"]

    data["alt"] = 0
    data["vspd"] = "..."
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "vspd" in resp.json["message"]

    with mock.patch(patch_path(_ENDPOINT), wraps=utils) as utils_patch:

        mock_sim_proxy = mock.MagicMock()
        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        utils_patch.sim_proxy.return_value = mock_sim_proxy

        # Test error from set_cleared_fl

        mock_sim_proxy.aircraft.set_cleared_fl.return_value = "Couldn't set CFL"

        data["vspd"] = 123

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't set CFL"

        # Test valid response

        mock_sim_proxy.aircraft.set_cleared_fl.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK


def test_alt_get(test_flask_client):
    """Tests the GET method"""

    # Test arg parsing

    resp = test_flask_client.get(f"{_ENDPOINT_PATH}?")
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.get(f"{_ENDPOINT_PATH}?{utils.CALLSIGN_LABEL}=T")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    with mock.patch(patch_path(_ENDPOINT), wraps=utils) as utils_patch:

        mock_sim_proxy = mock.MagicMock()
        utils_patch.sim_proxy.return_value = mock_sim_proxy
        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL

        # Test aircraft exists check

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        api_path = (
            f"{_ENDPOINT_PATH}?{utils.CALLSIGN_LABEL}={TEST_AIRCRAFT_PROPS.callsign}"
        )
        resp = test_flask_client.get(api_path)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test error response from get_properties

        utils_patch.check_exists.return_value = None
        mock_sim_proxy.aircraft.get_properties.return_value = "Error"

        resp = test_flask_client.get(api_path)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert (
            resp.data.decode()
            == f"Couldn't get properties for {TEST_AIRCRAFT_PROPS.callsign}: Error"
        )

        # Test valid response

        mock_sim_proxy.aircraft.get_properties.return_value = TEST_AIRCRAFT_PROPS

        resp = test_flask_client.get(api_path)
        assert resp.status_code == HTTPStatus.OK
        assert TEST_AIRCRAFT_PROPS.callsign in resp.json

        props = resp.json[TEST_AIRCRAFT_PROPS.callsign]
        assert props["fl_current"] == TEST_AIRCRAFT_PROPS.altitude.feet
        assert props["fl_cleared"] == TEST_AIRCRAFT_PROPS.cleared_flight_level.feet
        assert props["fl_requested"] == TEST_AIRCRAFT_PROPS.requested_flight_level.feet
