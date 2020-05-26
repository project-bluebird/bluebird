"""
Tests for the LISTROUTE endpoint
"""
from http import HTTPStatus
from unittest import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path

_ENDPOINT = "listroute"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_listroute_get(test_flask_client):
    """Tests the GET method"""

    endpoint_path = f"{_ENDPOINT_PATH}?{utils.CALLSIGN_LABEL}="

    # Test arg parsing

    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign_str = "A"
    resp = test_flask_client.get(f"{endpoint_path}{callsign_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test aircraft exists check

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        callsign_str = "TEST"
        resp = test_flask_client.get(f"{endpoint_path}{callsign_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test response when no route defined

        utils_patch.check_exists.return_value = None
        sim_proxy_mock.aircraft.route.return_value = "Aircraft has no route"

        resp = test_flask_client.get(f"{endpoint_path}{callsign_str}")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Aircraft has no route"

        # Test error from aircraft route

        sim_proxy_mock.aircraft.route.return_value = "Couldn't get route"

        resp = test_flask_client.get(f"{endpoint_path}{callsign_str}")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't get route"

        # Test valid response

        route_info = (
            "test_route",
            "FIRE",
            ["WATER", "FIRE", "EARTH"],
        )
        sim_proxy_mock.aircraft.route.return_value = route_info

        resp = test_flask_client.get(f"{endpoint_path}{callsign_str}")
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {
            utils.CALLSIGN_LABEL: "TEST",
            "route_name": route_info[0],
            "next_waypoint": route_info[1],
            "route_waypoints": route_info[2],
        }
