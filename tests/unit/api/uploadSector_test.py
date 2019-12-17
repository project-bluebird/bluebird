"""
Tests for the uploadSector endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


_ENDPOINT = f"{API_PREFIX}/uploadSector"


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, None, None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_uploadSector(test_flask_client, _set_bb_app):

    geoJSON = {"features": [{"type": "Feature", "geometry": {}, "properties": {"name": "test_sector", "type": "SECTOR", "children": {"SECTOR_VOLUME": {"names": ["221395673130872533"]}, "ROUTE": {"names": ["ASCENSION", "FALLEN"]}}}}, {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-0.2596527086555938, 51.08375683891335], [-0.26207557205922527, 51.916052359621695], [0.007075572059225247, 51.916052359621695], [0.004652708655593784, 51.08375683891335], [-0.2596527086555938, 51.08375683891335]]]}, "properties": {"name": "221395673130872533", "type": "SECTOR_VOLUME", "lower_limit": 60, "upper_limit": 460, "children": {}}}, {"type": "Feature", "properties": {"name": "ASCENSION", "type": "ROUTE", "children": {"FIX": {"names": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 50.91735552314281], [-0.1275, 51.08383154960228], [-0.1275, 51.49999999999135], [-0.1275, 51.916128869951486], [-0.1275, 52.08256690115545]]}}, {"type": "Feature", "properties": {"name": "FALLEN", "type": "ROUTE", "children": {"FIX": {"names": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"]}}}, "geometry": {"type": "LineString", "coordinates": [[-0.1275, 52.08256690115545], [-0.1275, 51.916128869951486], [-0.1275, 51.49999999999135], [-0.1275, 51.08383154960228], [-0.1275, 50.91735552314281]]}}, {"type": "Feature", "properties": {"name": "SPIRT", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 52.08256690115545]}}, {"type": "Feature", "properties": {"name": "AIR", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.916128869951486]}}, {"type": "Feature", "properties": {"name": "WATER", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.49999999999135]}}, {"type": "Feature", "properties": {"name": "EARTH", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 51.08383154960228]}}, {"type": "Feature", "properties": {"name": "FIYRE", "type": "FIX"}, "geometry": {"type": "Point", "coordinates": [-0.1275, 50.91735552314281]}}]}

    data = {"content": geoJSON}

    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.CREATED


def test():
    pytest.xfail("Implement tests, currently just a placeholder")
