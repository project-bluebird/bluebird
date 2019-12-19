"""
Tests for the uploadSector endpoint
"""

from http import HTTPStatus

from pytest import fixture

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/setSector"


@fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_setSector(test_flask_client, _set_bb_app):

    # Test error handling - content not provided

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT, json={})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test error handling - content did not pass validation check

    resp = test_flask_client.post(_ENDPOINT, json={"content": {}})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(
        _ENDPOINT,
        json={
            "content": {
                "features": [{"type": "", "properties": {}}]
            }  # missing geometry
        },
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test CREATED response

    resp = test_flask_client.post(_ENDPOINT, json={"content": {"features": []}})
    assert resp.status_code == HTTPStatus.CREATED

    resp = test_flask_client.post(
        _ENDPOINT,
        json={
            "content": {"features": [{"type": "", "geometry": {}, "properties": {}}]}
        },
    )
    assert resp.status_code == HTTPStatus.CREATED

    with open("sector_test.geojson", "r") as f:
        data = {"content": f.read()}

    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.CREATED
