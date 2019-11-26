"""
Tests for the scenario validation
"""

import json

from bluebird.api.resources.utils.scenario_validation import validate_json_scenario


def test_scenario_validation():
    with open("tests/data/overflier-climber-scenario-extended-60-22.json", "r") as f:
        assert not validate_json_scenario(json.load(f))
