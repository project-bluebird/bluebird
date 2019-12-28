"""
Tests for the sector validation
"""
import json

from aviary.sector.sector_element import SectorElement

from bluebird.api.resources.utils.sector_validation import validate_geojson_sector


def test_sector_validation():
    with open("tests/data/test_sector.geojson", "r") as f:
        assert isinstance(validate_geojson_sector(json.load(f)), SectorElement)
