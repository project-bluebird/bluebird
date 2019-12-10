"""
Tests for the sector validation
"""

import json

from bluebird.api.resources.utils.sector_validation import validate_geojson_sector


def test_sector_validation():
    with open("tests/data/sector-example_sector-I-150-400.geojson", "r") as f:
        assert not validate_geojson_sector(json.load(f))
