"""
Tests for the DIRECT endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils

from tests.unit import API_PREFIX


def test_direct_post(test_flask_client, patch_bb_app):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/direct"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {utils.CALLSIGN_LABEL: "T"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    data[utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "waypoint" in resp.json["message"]

    # Test waypoint check

    data["waypoint"] = None
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name not specified"

    data["waypoint"] = ""
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Waypoint name not specified"

    # Test callsign check

    data = {utils.CALLSIGN_LABEL: "XXX", "waypoint": "XXX"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Aircraft XXX was not found"

    # Test direct_to_waypoint

    data[utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Invalid waypoint"

    data["waypoint"] = "FIX"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
