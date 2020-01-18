"""
Tests for the scenario validation
"""
import json

from bluebird.utils.scenario_validation import validate_json_scenario
from tests.data import TEST_SCENARIO


def test_scenario_validation():
    with open(TEST_SCENARIO, "r") as f:
        assert not validate_json_scenario(json.load(f))
