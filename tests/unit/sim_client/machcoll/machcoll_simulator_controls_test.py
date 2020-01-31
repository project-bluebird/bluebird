"""
Tests for MachCollSimulatorControls
"""
import pytest

from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls

mc_simulator_controls = pytest.importorskip(
    "bluebird.sim_client.machcoll.machcoll_simulator_controls"
)


def test_abstract_class_implemented():
    """Tests that MachCollAircraftControls implements the abstract base class"""

    # Test basic instantiation
    mc_simulator_controls.MachCollSimulatorControls(None, None, None)

    # Test ABC exactly implemented
    assert AbstractSimulatorControls.__abstractmethods__ == {
        x
        for x in dir(mc_simulator_controls.MachCollSimulatorControls)
        if not x.startswith("_")
    }
