"""
Tests for the SECTOR endpoint
"""

from http import HTTPStatus

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/sector"


def test_sector(test_flask_client, monkeypatch):

    mock = MockBlueBird()
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)

    # Test error handling (no sector has been set)

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    # Test OK response (sector has been set)

    with open("sector_test.geojson", "r") as f:
        geoJSON = f.read()

    mock.sim_proxy.sector = geoJSON

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"sector": geoJSON}
