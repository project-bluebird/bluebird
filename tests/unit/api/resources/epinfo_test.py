"""
Tests for the EPINFO endpoint
"""

# NOTE(RKM 2019-12-28) This endpoint is currently disabled since it is now mostly
# covered by the "eplog" endpoint

from http import HTTPStatus

from tests.unit.api.resources import endpoint_path


_ENDPOINT = "epinfo"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_epinfo_get(test_flask_client):
    """Tests the GET method"""

    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.NOT_FOUND
