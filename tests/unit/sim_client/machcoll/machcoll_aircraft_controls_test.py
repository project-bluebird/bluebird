"""
Tests for MachCollAircraftControls
"""
from unittest import mock

import pytest

from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls

mc_aircraft_controls = pytest.importorskip(
    "bluebird.sim_client.machcoll.machcoll_aircraft_controls"
)


def test_abstract_class_implemented():
    """Tests that MachCollAircraftControls implements the abstract base class"""

    # Test basic instantiation
    mc_aircraft_controls.MachCollAircraftControls(mock.Mock())

    # Test ABC exactly implemented
    assert AbstractAircraftControls.__abstractmethods__ == {
        x
        for x in dir(mc_aircraft_controls.MachCollAircraftControls)
        if not x.startswith("_")
    }
