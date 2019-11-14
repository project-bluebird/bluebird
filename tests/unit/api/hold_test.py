"""
Tests for the HOLD endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX


def test_hold_post(test_flask_client, patch_bb_app):  # pylint: disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/hold"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.OK
