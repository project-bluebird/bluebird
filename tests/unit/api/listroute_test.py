"""
Tests for the LISTROUTE endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils
from tests.unit import API_PREFIX


def test_listroute_get(
    test_flask_client, patch_bb_app
):  # pylint: disable=unused-argument
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/listroute"

    # Test arg parsing

    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    callsign_str = "A"
    resp = test_flask_client.get(f"{endpoint}?{utils.CALLSIGN_LABEL}={callsign_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    callsign_str = "AAA"
    resp = test_flask_client.get(f"{endpoint}?{utils.CALLSIGN_LABEL}={callsign_str}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f"Aircraft {callsign_str} was not found"

    callsign_str = "TEST"
    resp = test_flask_client.get(f"{endpoint}?{utils.CALLSIGN_LABEL}={callsign_str}")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Could not get aircraft route"

    resp = test_flask_client.get(f"{endpoint}?{utils.CALLSIGN_LABEL}={callsign_str}")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {utils.CALLSIGN_LABEL: callsign_str, "route": ["A", "B"]}
