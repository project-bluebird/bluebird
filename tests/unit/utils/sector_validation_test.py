"""
Tests for the sector validation
"""
from aviary.sector.sector_element import SectorElement

from bluebird.utils.sector_validation import validate_geojson_sector
from tests.data import TEST_SECTOR


def test_sector_validation():
    assert isinstance(validate_geojson_sector(TEST_SECTOR), SectorElement)
