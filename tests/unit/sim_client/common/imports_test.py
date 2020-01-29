"""
Contains common tests for importing the sim_client modules
"""
import importlib

from bluebird.sim_client import AbstractSimClient

# NOTE: These functions aren't actually tests! They are imported and called with the sim
# names


def sim_client_module_import(sim_name: str):
    """Test that the module can be imported without error"""
    importlib.import_module(f"bluebird.sim_client.{sim_name.lower()}.sim_client")


def sim_client_instantiation(sim_name: str):
    """Tests that the SimClient can be instantiated"""
    module = importlib.import_module(
        f"bluebird.sim_client.{sim_name.lower()}.sim_client"
    )
    sim_client_class = getattr(module, "SimClient")
    sim_client_class()

    # Test ABC exactly implemented
    assert AbstractSimClient.__abstractmethods__ == {
        x for x in dir(sim_client_class) if not x.startswith("_")
    }
