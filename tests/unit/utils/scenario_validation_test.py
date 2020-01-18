"""
Tests for the scenario validation
"""
from bluebird.utils.scenario_validation import validate_json_scenario
from tests.data import TEST_SCENARIO


def test_scenario_validation():
    assert not validate_json_scenario(TEST_SCENARIO)
