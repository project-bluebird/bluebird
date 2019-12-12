"""
Tests for BlueBird's built-in metrics (provided by Aviary)
"""

import pytest
import mock

import bluebird.metrics.bluebird.metrics as metrics
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


def test_pairwise_separation_metric():
    """
    Tests the pairwise_separation_metric function
    """

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)

    # Test invalid args

    with pytest.raises(AssertionError, match="Expected 2 string arguments"):
        metrics.pairwise_separation_metric(mock_aircraft_controls, None, None)

    with pytest.raises(AssertionError, match="Invalid callsign ''"):
        metrics.pairwise_separation_metric(mock_aircraft_controls, "", "")
    # Test result with valid args


def test_sector_exit_metric():
    """
    Tests the sector_exit_metric function
    """

    # Test invalid args

    # Test result with valid args
