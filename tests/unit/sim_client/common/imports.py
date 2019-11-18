"""
Contains common tests for importing the sim_client modules
"""

import importlib

# NOTE: These two aren't actually tests! They are imported and called with the sim names


def sim_client_module_import(sim_name: str):
    """Test that the module can be imported without error"""
    importlib.import_module(f"bluebird.sim_client.{sim_name.lower()}.sim_client")


def abstract_class_implementation(sim_name: str):
    """Tests that the abstract classes are properly implemented"""
    module = importlib.import_module(
        f"bluebird.sim_client.{sim_name.lower()}.sim_client"
    )
    getattr(module, f"{sim_name}AircraftControls")(None)
    getattr(module, f"{sim_name}SimulatorControls")(None)
    getattr(module, f"{sim_name}WaypointControls")(None)
