"""
Tests for the MachColl sim client module
"""
import pytest

from tests.unit.sim_client.common.imports_test import sim_client_instantiation


_MODULE_NAME = "MachColl"


mc_aircraft_controls = pytest.importorskip(
    "bluebird.sim_client.machcoll.machcoll_aircraft_controls"
)


def test_sim_client_instantiation():
    """Tests that the SimClient can be instantiated"""
    sim_client_instantiation(_MODULE_NAME)
