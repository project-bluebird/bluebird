"""
Tests for the MachColl sim client module
"""
import pytest

from bluebird.metrics import MetricsProviders
from tests.unit.sim_client.common.imports_test import sim_client_instantiation


_MODULE_NAME = "MachColl"


mc_aircraft_controls = pytest.importorskip(
    "bluebird.sim_client.machcoll.machcoll_aircraft_controls"
)


def test_sim_client_instantiation():
    """Tests that the SimClient can be instantiated"""

    class FakeProvider:
        def __str__(self):
            return "MachColl"

        @property
        def metrics(self):
            return []

    sim_client_instantiation(
        _MODULE_NAME, MetricsProviders([FakeProvider()]), extra_methods={"mc_client"}
    )
