"""
Tests for the DTMULT endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX


def test_dtmult_post(
    test_flask_client, patch_sim_proxy
):  # pylint:disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/dtmult"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test multiplier check

    data = {"multiplier": -1}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Multiplier must be greater than 0"

    # Test set_sim_speed

    data = {"multiplier": 100}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Requested speed too large"

    data = {"multiplier": 10}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK
