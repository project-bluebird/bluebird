"""
Tests for the SECTOR endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/sector"


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, None, None)
    mock.sim_proxy.sector = {}
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_sector(test_flask_client, _set_bb_app):

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK


def test():
    pytest.xfail("Implement tests, currently just a placeholder")
