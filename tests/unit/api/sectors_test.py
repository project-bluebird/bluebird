"""
Tests for the SECTORS endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/sectors"

class MockSimulatorControls:
    # TODO (RJ 2019-12-16) Will need - supload_new_sector?
    pass


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_sectors(test_flask_client, _set_bb_app):
    pytest.xfail("Skip until sectors returns GeoJSON")
