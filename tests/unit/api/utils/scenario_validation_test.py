"""
Tests for the scenario validation
"""

import json

from bluebird.api.resources.utils.scenario_validation import validate_json_scenario


def test_scenario_validation():
    with open("tests/data/test_scenario.json", "r") as f:
        assert not validate_json_scenario(json.load(f))
