"""
Tests for the RESET endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX


class MockSimulatorControls:
    def __init__(self):
        self._reset_flag = False

    def reset(self):
        if not self._reset_flag:
            self._reset_flag = True
            return "Error: Couldn't reset sim"
        return None


def test_reset_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/reset"

    # Test mode check

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't reset sim"

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.OK
