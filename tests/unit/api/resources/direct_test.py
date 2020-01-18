"""
Tests for the DIRECT endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils

from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import TEST_WAYPOINT
from tests.unit.api.resources import get_app_mock


_ENDPOINT = "direct"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_direct_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {utils.CALLSIGN_LABEL: "T"}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data[utils.CALLSIGN_LABEL] = "FAKE"
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test name check

    data["waypoint"] = ""
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name must be specified"

    # Test waypoint exists check

    app_mock = get_app_mock(test_flask_client)
    app_mock.sim_proxy.simulation.find_waypoint.return_value = None

    data["waypoint"] = TEST_WAYPOINT.name
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f"Could not find waypoint {TEST_WAYPOINT.name}"

    # Test callsign check

    app_mock.sim_proxy.simulation.find_waypoint.return_value = TEST_WAYPOINT
    app_mock.sim_proxy.aircraft.exists.return_value = False
    print(f"TEST: {app_mock.sim_proxy.aircraft.exists}")
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    # Test error from direct_to_waypoint

    app_mock.sim_proxy.aircraft.exists.return_value = True
    app_mock.sim_proxy.aircraft.direct_to_waypoint.return_value = "Error"

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error"

    # Test valid response

    app_mock.sim_proxy.aircraft.direct_to_waypoint.return_value = None

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.OK
