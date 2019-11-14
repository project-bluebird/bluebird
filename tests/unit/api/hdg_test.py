"""
Tests for the HDG endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as utils

from tests.unit import API_PREFIX


def test_hdg_post(test_flask_client, patch_sim_proxy):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/hdg"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {utils.CALLSIGN_LABEL: "FAKE"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["hdg"] = "aaa"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test set_heading NotImplementedError

    data["hdg"] = 123
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.NOT_IMPLEMENTED

    # Test set_heading called

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Invalid callsign"

    data[utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
