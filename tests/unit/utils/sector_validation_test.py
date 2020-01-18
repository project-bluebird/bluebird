"""
Tests for the sector validation
"""
import json

from aviary.sector.sector_element import SectorElement

from bluebird.utils.sector_validation import validate_geojson_sector
from tests.data import TEST_SECTOR


def test_sector_validation():
    with open(TEST_SECTOR, "r") as f:
        assert isinstance(validate_geojson_sector(json.load(f)), SectorElement)
