"""
Tests for the HDG endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as api_utils
import bluebird.utils.types as types

from tests.unit import API_PREFIX


class MockAircraftControls:
    def __init__(self):
        self._set_heading_called = 0

    def exists(self, callsign: types.Callsign):
        assert isinstance(callsign, types.Callsign)
        # "TEST*" aircraft exist, all others do not
        return str(callsign).upper().startswith("TEST")

    def set_heading(self, callsign: types.Callsign, heading: types.Heading):
        assert isinstance(callsign, types.Callsign)
        assert isinstance(heading, types.Heading)
        if not self._set_heading_called:
            self._set_heading_called += 1
            raise NotImplementedError
        self._set_heading_called += 1
        return "Error: Couldn't set heading" if self._set_heading_called < 3 else None


def test_hdg_post(test_flask_client, _set_bb_app):
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/hdg"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {api_utils.CALLSIGN_LABEL: "FAKE"}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data["hdg"] = "aaa"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test aircraft exists check

    data["hdg"] = 123
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == 'Aircraft "FAKE" does not exist'

    # Test set_heading NotImplementedError

    data[api_utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.NOT_IMPLEMENTED

    # Test set_heading called

    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error: Couldn't set heading"

    data[api_utils.CALLSIGN_LABEL] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.OK