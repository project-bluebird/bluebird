"""
Tests for BlueSkyAircraftControls
"""
import mock

from bluebird.sim_client.bluesky.bluesky_aircraft_controls import (
    BlueSkyAircraftControls,
)
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


def test_abstract_class_implemented():
    """Tests that BlueSkyAircraftControls implements the abstract base class"""

    # Test basic instantiation
    BlueSkyAircraftControls(mock.Mock())

    # Test ABC exactly implemented
    assert AbstractAircraftControls.__abstractmethods__ == {
        x for x in dir(BlueSkyAircraftControls) if not x.startswith("_")
    }
